from __future__ import annotations

import argparse
import shutil
import ssl
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from datasets import Image, load_dataset


DATASET_SOURCES = {
    "AID": {
        "mode": "url",
        "url": "https://1drv.ms/u/s!AthY3vMZmuxChNR0Co7QHpJ56M-SvQ",
        "filename": "AID.zip",
        "source_note": "Official AID page -> OneDrive",
    },
    "UCMerced": {
        "mode": "url",
        "url": "http://weegee.vision.ucmerced.edu/datasets/UCMerced_LandUse.zip",
        "filename": "UCMerced_LandUse.zip",
        "source_note": "Official UCMerced page -> direct zip",
    },
    "NWPU_RESISC45": {
        "mode": "hf_dataset",
        "repo_id": "jonathan-roberts1/NWPU-RESISC45",
        "split": "train",
        "image_column": "image",
        "label_name_column": "label_name",
        "label_column": "label",
        "filename_prefix": "nwpu",
        "source_note": "Official NWPU page + Hugging Face mirror",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download official remote sensing datasets.")
    parser.add_argument("--dataset", required=True, choices=sorted(DATASET_SOURCES))
    parser.add_argument(
        "--output-dir",
        default="data/raw_downloads",
        help="Directory used to store downloaded archives.",
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Only test connectivity and print resolved metadata without saving the file.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL verification. Only use this if the official endpoint has TLS issues.",
    )
    parser.add_argument(
        "--dataset-root",
        default="data/raw",
        help="Directory used to store extracted class-folder datasets for Hugging Face mirrors.",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Optional Hugging Face cache directory.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Optional limit for materializing only the first N samples. Useful for smoke tests.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing target dataset folder when materializing Hugging Face mirrors.",
    )
    return parser.parse_args()


def build_ssl_context(insecure: bool):
    if not insecure:
        return None
    return ssl._create_unverified_context()


def resolve_filename(response, fallback: str) -> str:
    content_disposition = response.headers.get("Content-Disposition", "")
    if "filename=" in content_disposition:
        filename = content_disposition.split("filename=", 1)[1].strip().strip('"')
        if filename:
            return filename
    return fallback


def _copy_image_payload(image_payload: dict, output_path: Path) -> None:
    image_bytes = image_payload.get("bytes")
    if image_bytes is not None:
        output_path.write_bytes(image_bytes)
        return

    source_path = image_payload.get("path")
    if source_path:
        shutil.copyfile(source_path, output_path)
        return

    raise ValueError("Image payload does not contain bytes or path.")


def _resolve_label_name(dataset, row: dict, entry: dict) -> str:
    label_name_column = entry.get("label_name_column")
    if label_name_column and label_name_column in row and row[label_name_column] is not None:
        return str(row[label_name_column])

    label_column = entry.get("label_column", "label")
    if label_column in row:
        feature = dataset.features.get(label_column)
        if feature is not None and hasattr(feature, "names"):
            label_value = int(row[label_column])
            return str(feature.names[label_value])
        return str(row[label_column])

    raise KeyError("Could not resolve label name from dataset row.")


def download_hf_dataset(args: argparse.Namespace, entry: dict) -> None:
    dataset_root = Path(args.dataset_root).resolve()
    target_root = dataset_root / args.dataset

    if target_root.exists() and any(target_root.iterdir()) and not args.overwrite:
        print(f"target_exists={target_root}")
        print("hint=use --overwrite if you want to rebuild the directory")
        return

    if args.overwrite and target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset(
        entry["repo_id"],
        split=entry.get("split", "train"),
        cache_dir=args.cache_dir,
    )
    image_column = entry.get("image_column", "image")
    dataset = dataset.cast_column(image_column, Image(decode=False))

    column_names = list(dataset.column_names)
    num_rows = len(dataset)
    class_names = set()

    print(f"dataset={args.dataset}")
    print(f"source_note={entry['source_note']}")
    print(f"repo_id={entry['repo_id']}")
    print(f"split={entry.get('split', 'train')}")
    print(f"rows={num_rows}")
    print(f"columns={column_names}")
    print(f"target_root={target_root}")

    if args.probe:
        preview = dataset[0]
        preview_label = _resolve_label_name(dataset, preview, entry)
        print(f"preview_label={preview_label}")
        print(f"preview_image_keys={sorted(preview[image_column].keys())}")
        return

    written = 0
    max_samples = args.max_samples if args.max_samples and args.max_samples > 0 else None
    for index, row in enumerate(dataset):
        label_name = _resolve_label_name(dataset, row, entry)
        class_names.add(label_name)
        class_dir = target_root / label_name
        class_dir.mkdir(parents=True, exist_ok=True)

        image_payload = row[image_column]
        original_path = image_payload.get("path") or ""
        suffix = Path(original_path).suffix.lower() or ".jpg"
        output_path = class_dir / f"{entry.get('filename_prefix', 'sample')}_{index:05d}{suffix}"
        _copy_image_payload(image_payload, output_path)

        written += 1
        if written % 500 == 0:
            print(f"materialized={written}", flush=True)
        if max_samples is not None and written >= max_samples:
            break

    print(f"materialized={written}")
    print(f"classes={len(class_names)}")
    print(f"saved_to={target_root}")


def download_url_dataset(args: argparse.Namespace, entry: dict) -> None:
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    request = Request(
        entry["url"],
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PythonDatasetDownloader/1.0"
        },
    )

    try:
        with urlopen(
            request,
            timeout=60,
            context=build_ssl_context(args.insecure),
        ) as response:
            final_url = response.geturl()
            filename = resolve_filename(response, entry["filename"])
            content_type = response.headers.get("Content-Type", "unknown")
            content_length = response.headers.get("Content-Length", "unknown")

            print(f"dataset={args.dataset}")
            print(f"source_note={entry['source_note']}")
            print(f"requested_url={entry['url']}")
            print(f"final_url={final_url}")
            print(f"content_type={content_type}")
            print(f"content_length={content_length}")
            print(f"filename={filename}")

            if args.probe:
                return

            output_path = output_dir / filename
            total = int(content_length) if str(content_length).isdigit() else None
            downloaded = 0

            with output_path.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = downloaded * 100 / total
                        print(
                            f"downloaded={downloaded}/{total} ({percent:.2f}%)",
                            flush=True,
                        )
                    else:
                        print(f"downloaded={downloaded}", flush=True)

            print(f"saved_to={output_path}")
    except HTTPError as exc:
        print(f"http_error={exc.code}")
        print(f"reason={exc.reason}")
        sys.exit(1)
    except URLError as exc:
        print(f"url_error={exc.reason}")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - operational helper
        print(f"error={exc}")
        sys.exit(1)


def main() -> None:
    args = parse_args()
    entry = DATASET_SOURCES[args.dataset]
    mode = entry.get("mode", "url")
    if mode == "hf_dataset":
        download_hf_dataset(args, entry)
        return
    download_url_dataset(args, entry)


if __name__ == "__main__":
    main()

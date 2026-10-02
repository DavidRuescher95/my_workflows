#!/usr/bin/env python3
"""Validate an MGF file and split complete feature groups into chunks.

Example:
    python split_mgf.py input.mgf chunks 10000
"""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FeatureGroup:
    """Consecutive spectra sharing one FEATURE_ID."""

    feature_id: str
    spectra: tuple[tuple[str, ...], ...]


def read_feature_groups(input_mgf: Path) -> tuple[tuple[str, ...], list[FeatureGroup]]:
    """Parse and validate an MGF, preserving complete feature groups.

    Example:
        preamble, groups = read_feature_groups(Path("input.mgf"))
    """
    preamble: list[str] = []
    spectra: list[tuple[str, tuple[str, ...]]] = []
    current_spectrum: list[str] | None = None
    seen_spectrum = False

    with input_mgf.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            marker = line.strip()
            if marker == "BEGIN IONS":
                if current_spectrum is not None:
                    raise ValueError(f"{input_mgf}:{line_number}: nested BEGIN IONS")
                current_spectrum = [line]
                seen_spectrum = True
            elif marker == "END IONS":
                if current_spectrum is None:
                    raise ValueError(f"{input_mgf}:{line_number}: END IONS without BEGIN IONS")
                current_spectrum.append(line)
                feature_ids = [
                    item.split("=", 1)[1].strip()
                    for item in current_spectrum
                    if item.startswith("FEATURE_ID=")
                ]
                if len(feature_ids) != 1 or not feature_ids[0]:
                    raise ValueError(
                        f"{input_mgf}:{line_number}: spectrum must contain exactly one "
                        "non-empty FEATURE_ID"
                    )
                spectra.append((feature_ids[0], tuple(current_spectrum)))
                current_spectrum = None
            elif current_spectrum is not None:
                current_spectrum.append(line)
            elif not seen_spectrum:
                preamble.append(line)
            elif marker:
                raise ValueError(
                    f"{input_mgf}:{line_number}: content found outside an ion block"
                )

    if current_spectrum is not None:
        raise ValueError(f"{input_mgf}: spectrum is missing END IONS")
    if not spectra:
        raise ValueError(f"{input_mgf}: no ion spectra found")

    groups: list[FeatureGroup] = []
    closed_feature_ids: set[str] = set()
    for feature_id, spectrum in spectra:
        if groups and groups[-1].feature_id == feature_id:
            previous = groups[-1]
            groups[-1] = FeatureGroup(feature_id, previous.spectra + (spectrum,))
            continue
        if feature_id in closed_feature_ids:
            raise ValueError(
                f"{input_mgf}: FEATURE_ID {feature_id!r} occurs in noncontiguous blocks"
            )
        if groups:
            closed_feature_ids.add(groups[-1].feature_id)
        groups.append(FeatureGroup(feature_id, (spectrum,)))

    return tuple(preamble), groups


def write_chunks(
    input_mgf: Path,
    output_dir: Path,
    features_per_chunk: int,
) -> dict[str, object]:
    """Write validated feature chunks and return their manifest.

    Example:
        manifest = write_chunks(Path("input.mgf"), Path("chunks"), 10000)
    """
    if features_per_chunk <= 0:
        raise ValueError("features_per_chunk must be a positive integer")

    preamble, groups = read_feature_groups(input_mgf)
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale_chunk in output_dir.glob("chunk_*.mgf"):
        stale_chunk.unlink()

    chunks: list[dict[str, object]] = []
    for offset in range(0, len(groups), features_per_chunk):
        chunk_groups = groups[offset : offset + features_per_chunk]
        chunk_name = f"chunk_{len(chunks) + 1:03d}.mgf"
        chunk_path = output_dir / chunk_name
        with chunk_path.open("w", encoding="utf-8") as output:
            output.writelines(preamble)
            for group in chunk_groups:
                for spectrum in group.spectra:
                    output.writelines(spectrum)
        chunks.append(
            {
                "file": chunk_name,
                "feature_count": len(chunk_groups),
                "spectrum_count": sum(len(group.spectra) for group in chunk_groups),
            }
        )

    return {
        "input": str(input_mgf.resolve()),
        "feature_count": len(groups),
        "spectrum_count": sum(len(group.spectra) for group in groups),
        "features_per_chunk": features_per_chunk,
        "chunks": chunks,
    }


def main() -> None:
    """Run MGF validation and chunk generation from the command line."""
    parser = argparse.ArgumentParser(
        description="Validate an MGF and split complete feature groups into chunks."
    )
    parser.add_argument("input_mgf", type=Path, help="Input MGF file")
    parser.add_argument("out_dir", type=Path, help="Directory for output chunks")
    parser.add_argument("features_per_chunk", type=int, help="Maximum features per chunk")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Manifest path (default: <out_dir>/manifest.json)",
    )
    args = parser.parse_args()

    if not args.input_mgf.is_file():
        parser.error(f"input file does not exist: {args.input_mgf}")
    if args.input_mgf.suffix.lower() != ".mgf":
        parser.error("input file must have the .mgf extension")

    try:
        manifest = write_chunks(args.input_mgf, args.out_dir, args.features_per_chunk)
        manifest_path = args.manifest or args.out_dir / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
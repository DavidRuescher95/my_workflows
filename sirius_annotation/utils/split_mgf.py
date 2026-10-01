#!/usr/bin/env python3
import argparse
from pathlib import Path


def main():
    """Split an MGF file into feature chunks; each feature stays in one chunk."""
    parser = argparse.ArgumentParser(description="Split an MGF file into feature chunks.")
    parser.add_argument("input_mgf", type=Path, help="Input MGF file")
    parser.add_argument("out_dir", type=Path, help="Directory for output chunks")
    parser.add_argument("features_per_chunk", type=int, help="Maximum features per chunk")
    args = parser.parse_args()

    if args.features_per_chunk <= 0:
        parser.error("features_per_chunk must be a positive integer")

    chunk_idx = 1
    feature_count = 0
    current_feature = None
    current_feature_block = []
    out = None

    def write_feature(feature_block):
        nonlocal chunk_idx, feature_count, out

        if feature_count >= args.features_per_chunk:
            out.close()
            chunk_idx += 1
            out = (args.out_dir / f"chunk_{chunk_idx:03d}.mgf").open("w")
            feature_count = 0

        out.writelines(feature_block)
        feature_count += 1

    try:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        with args.input_mgf.open() as source:
            out = (args.out_dir / f"chunk_{chunk_idx:03d}.mgf").open("w")
            spectrum = []
            inside = False

            for line in source:
                if line.startswith("BEGIN IONS"):
                    spectrum = [line]
                    inside = True

                elif inside:
                    spectrum.append(line)

                    if line.startswith("END IONS"):
                        inside = False

                        feature_id = None
                        for spectrum_line in spectrum:
                            if spectrum_line.startswith("FEATURE_ID="):
                                feature_id = spectrum_line.strip().split("=", 1)[1]
                                break

                        if feature_id is None:
                            raise ValueError(f"{args.input_mgf}: spectrum missing FEATURE_ID")

                        if current_feature is None:
                            current_feature = feature_id

                        if feature_id != current_feature:
                            # Flush only complete feature groups so their spectra stay together.
                            write_feature(current_feature_block)
                            current_feature_block = []
                            current_feature = feature_id

                        current_feature_block.extend(spectrum)

            if inside:
                raise ValueError(f"{args.input_mgf}: spectrum is missing END IONS")

        if current_feature_block:
            write_feature(current_feature_block)
    except OSError as error:
        parser.error(f"I/O error: {error}")
    except ValueError as error:
        parser.error(str(error))
    finally:
        if out is not None:
            out.close()


if __name__ == "__main__":
    main()
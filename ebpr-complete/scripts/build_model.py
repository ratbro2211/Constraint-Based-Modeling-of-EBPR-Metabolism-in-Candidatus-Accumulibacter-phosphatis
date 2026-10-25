"""Build and serialize the default anaerobic teaching-model configuration."""

from cobra.io import save_json_model

from ebpr_model import ROOT, build_model


def main() -> None:
    destination = ROOT / "models" / "ebpr_model.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    save_json_model(build_model("anaerobic"), str(destination))
    print(f"Saved default anaerobic model to {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

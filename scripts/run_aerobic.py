"""Run the stored-PHA-fed aerobic EBPR phase."""

from ebpr_model import build_model, optimize_phase, print_summary, write_fluxes


def main() -> None:
    model = build_model("aerobic")
    solution = optimize_phase(model)
    print_summary(model, solution)
    output = write_fluxes(model, solution, "aerobic_fluxes.csv")
    print(f"Reaction fluxes written to {output}")


if __name__ == "__main__":
    main()

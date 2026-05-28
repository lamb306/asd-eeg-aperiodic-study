from pathlib import Path
import shutil
import zipfile
import tempfile
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import patches


ROOT = Path(r"d:\asd_eeg_aperiodic_study")
DOCX = ROOT / "manuscript_submission_final.docx"
BACKUP = ROOT / "manuscript_submission_final_before_figure1B_beauty_fix.docx"
FIG_DIR = ROOT / "figures_submission_final"
FIG1_PNG = FIG_DIR / "Figure1.png"
FIG1_PDF = FIG_DIR / "Figure1.pdf"


def setup_style():
    mpl.rcParams["font.family"] = ["Arial", "DejaVu Sans", "sans-serif"]
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42


def draw_panel_label(ax, label):
    ax.text(0.01, 0.99, label, transform=ax.transAxes, ha="left", va="top", fontsize=14, fontweight="bold")


def rounded_box(ax, x, y, w, h, text, fc, ec, fontsize=9.5):
    rect = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.02",
        facecolor=fc,
        edgecolor=ec,
        linewidth=1.2,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize)


def draw_figure1():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axs = plt.subplots(1, 3, figsize=(16.0, 5.4))

    # Panel A
    ax = axs[0]
    draw_panel_label(ax, "A")
    ax.axis("off")
    rounded_box(ax, 0.10, 0.74, 0.80, 0.17, "Initial sample\nN = 168", "#f5f5f5", "#5a5a5a", fontsize=10)
    rounded_box(ax, 0.10, 0.47, 0.80, 0.17, "Usable artifact-free epochs ≥ 60\nN = 145", "#f5f5f5", "#5a5a5a", fontsize=10)
    rounded_box(
        ax,
        0.10,
        0.20,
        0.80,
        0.17,
        "Passed spectral-parameterization QC\nN = 138\nASD = 61, TD = 77",
        "#f5f5f5",
        "#5a5a5a",
        fontsize=9.6,
    )
    ax.annotate("", xy=(0.50, 0.72), xytext=(0.50, 0.66), arrowprops=dict(arrowstyle="->", lw=1.2, color="#4a4a4a"))
    ax.annotate("", xy=(0.50, 0.45), xytext=(0.50, 0.39), arrowprops=dict(arrowstyle="->", lw=1.2, color="#4a4a4a"))

    # Panel B (beautified two-row pipeline)
    ax = axs[1]
    draw_panel_label(ax, "B")
    ax.axis("off")
    top_fc = "#eaf2ff"
    bot_fc = "#edf8f0"
    edge = "#2b6cb0"

    # Row 1
    w1, h1, y1 = 0.26, 0.18, 0.64
    x_top = [0.03, 0.37, 0.71]
    t_top = ["Resting-state EEG", "Spectral\nparameterization", "Aperiodic metrics"]
    for x, t in zip(x_top, t_top):
        rounded_box(ax, x, y1, w1, h1, t, top_fc, edge, fontsize=9.6)
    ax.annotate("", xy=(x_top[1] - 0.02, y1 + h1 / 2), xytext=(x_top[0] + w1 + 0.02, y1 + h1 / 2), arrowprops=dict(arrowstyle="->", lw=1.3, color=edge))
    ax.annotate("", xy=(x_top[2] - 0.02, y1 + h1 / 2), xytext=(x_top[1] + w1 + 0.02, y1 + h1 / 2), arrowprops=dict(arrowstyle="->", lw=1.3, color=edge))

    # Row 2
    w2, h2, y2 = 0.34, 0.18, 0.26
    x_bot = [0.11, 0.55]
    t_bot = ["Naturalistic movie ISC", "Cross-state coupling"]
    for x, t in zip(x_bot, t_bot):
        rounded_box(ax, x, y2, w2, h2, t, bot_fc, "#2f855a", fontsize=9.8)
    ax.annotate("", xy=(x_bot[1] - 0.02, y2 + h2 / 2), xytext=(x_bot[0] + w2 + 0.02, y2 + h2 / 2), arrowprops=dict(arrowstyle="->", lw=1.3, color="#2f855a"))

    # Cross-row connector from top-right to bottom-left
    ax.annotate(
        "",
        xy=(x_bot[0] + w2 * 0.50, y2 + h2 + 0.02),
        xytext=(x_top[2] + w1 * 0.50, y1 - 0.02),
        arrowprops=dict(arrowstyle="->", lw=1.3, color="#4a5568", connectionstyle="arc3,rad=0.0"),
    )

    # Panel C
    ax = axs[2]
    draw_panel_label(ax, "C")
    labels = [
        "Resting-state primary analysis",
        "Movie ISC event analysis",
        "Coupling primary analysis",
        "Stringent-inclusion sensitivity analysis",
    ]
    vals = [138, 169, 128, 102]
    colors = ["#4c78a8", "#72b7b2", "#f58518", "#54a24b"]
    ax.barh(labels, vals, color=colors)
    for i, v in enumerate(vals):
        ax.text(v + 1.8, i, f"n = {v}", va="center", fontsize=9)
    ax.set_xlim(0, 185)
    ax.set_xlabel("Number of participants", fontsize=9)
    ax.tick_params(axis="both", labelsize=8)
    ax.grid(axis="x", alpha=0.2)

    fig.subplots_adjust(left=0.05, right=0.98, wspace=0.30)
    fig.savefig(FIG1_PNG, dpi=600, bbox_inches="tight")
    fig.savefig(FIG1_PDF, dpi=600, bbox_inches="tight")
    plt.close(fig)


def patch_docx_image1():
    shutil.copy2(DOCX, BACKUP)
    tmp_fd, tmp_name = tempfile.mkstemp(suffix=".docx", dir=str(ROOT))
    import os
    os.close(tmp_fd)
    Path(tmp_name).unlink(missing_ok=True)
    tmp_path = Path(tmp_name)

    with zipfile.ZipFile(DOCX, "r") as zin, zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/media/image1.png":
                data = FIG1_PNG.read_bytes()
            zout.writestr(item, data)

    shutil.copy2(tmp_path, DOCX)
    tmp_path.unlink(missing_ok=True)


def main():
    setup_style()
    draw_figure1()
    patch_docx_image1()
    print("figure1_redrawn=True")
    print(f"saved_png={FIG1_PNG}")
    print(f"saved_pdf={FIG1_PDF}")
    print(f"docx_patched={DOCX}")
    print(f"backup={BACKUP}")


if __name__ == "__main__":
    main()

import matplotlib.pyplot as plt
import tempfile

PRIMARY = "#10012c"
SECONDARY = "#2ED3C6"
ACCENT = "#F5B301"
TEXT = "#FFFFFF"


def gerar_grafico_gastos_por_categoria(data):
    categorias = [row[0] if row[0] else "Sem categoria" for row in data]
    valores = [row[1] if row[1] else 0 for row in data]

    plt.figure(figsize=(9, 5), facecolor=PRIMARY)
    ax = plt.gca()
    ax.set_facecolor(PRIMARY)

    bars = plt.bar(
        categorias,
        valores,
        color=SECONDARY,
        edgecolor=ACCENT,
        linewidth=1.5
    )

    plt.xlabel("Categoria", color=TEXT, fontsize=11)
    plt.ylabel("Total Gasto (R$)", color=TEXT, fontsize=11)
    plt.title("Gastos por Categoria", color=ACCENT, fontsize=14, weight="bold")

    plt.grid(axis="y", linestyle="--", alpha=0.2, color=TEXT)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(TEXT)
    ax.spines["bottom"].set_color(TEXT)

    ax.tick_params(axis="x", colors=TEXT)
    ax.tick_params(axis="y", colors=TEXT)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"R$ {height:.2f}".replace(".", ","),
            ha="center",
            va="bottom",
            color=TEXT,
            fontsize=9
        )

    plt.tight_layout()

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(
        temp_file.name,
        dpi=150,
        bbox_inches="tight",
        facecolor=PRIMARY
    )
    plt.close()

    return temp_file.name

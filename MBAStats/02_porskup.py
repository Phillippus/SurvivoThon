import io
import sys
from typing import List

try:
    import pandas as pd
except ModuleNotFoundError:
    print(
        "Chýba balík 'pandas'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install pandas streamlit scipy openpyxl odfpy"
    )
    raise SystemExit(1)

try:
    import streamlit as st
except ModuleNotFoundError:
    print(
        "Chýba balík 'streamlit'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install streamlit"
    )
    raise SystemExit(1)

try:
    from scipy.stats import mannwhitneyu, kruskal
except ModuleNotFoundError:
    print(
        "Chýba balík 'scipy'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install scipy"
    )
    raise SystemExit(1)


st.set_page_config(page_title="Porovnanie skupín", layout="wide")


def load_data(uploaded_file) -> pd.DataFrame:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    if file_name.endswith(".ods"):
        return pd.read_excel(uploaded_file, engine="odf")

    raise ValueError("Podporované formáty sú: CSV, XLSX, ODS.")


def add_grouped_profession_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ak dataset obsahuje stĺpec 'profesia', vytvorí pomocný zlúčený stĺpec
    'profesia_3g' so skupinami Lekár, Sestra a Iné/Ostatné.
    """
    if "profesia" not in df.columns:
        return df

    work_df = df.copy()
    mapping = {
        "Lekár": "Lekár",
        "Sestra": "Sestra",
        "Sestra / Inštrumentárka": "Sestra",
        "Sanitár / Praktická sestra": "Iné/Ostatné",
        "Iné zdravotnícke povolanie": "Iné/Ostatné",
    }
    work_df["profesia_3g"] = work_df["profesia"].map(mapping).fillna(work_df["profesia"])
    return work_df


def group_summary(df: pd.DataFrame, group_col: str, score_col: str) -> pd.DataFrame:
    rows = []
    for group_name, group_df in df.groupby(group_col, dropna=True):
        values = group_df[score_col].dropna()
        if len(values) == 0:
            continue
        rows.append(
            {
                "skupina": group_name,
                "n": int(len(values)),
                "priemer": float(values.mean()),
                "median": float(values.median()),
                "minimum": float(values.min()),
                "maximum": float(values.max()),
            }
        )
    return pd.DataFrame(rows)


st.title("Porovnanie skupín")
st.write(
    "Nahraj dátový súbor a aplikácia porovná skupiny pomocou Mann–Whitneyho U testu alebo Kruskalovho–Wallisovho testu."
)

uploaded_file = st.file_uploader(
    "Nahraj CSV / XLSX / ODS súbor",
    type=["csv", "xlsx", "ods"],
)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Súbor sa nepodarilo načítať: {e}")
        st.stop()
    df = add_grouped_profession_column(df)

    st.subheader("Náhľad dát")
    st.dataframe(df.head(20), use_container_width=True)

    st.write(f"Počet riadkov: **{df.shape[0]}**")
    st.write(f"Počet stĺpcov: **{df.shape[1]}**")

    numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    categorical_columns = [col for col in df.columns if col not in numeric_columns]

    if not numeric_columns:
        st.warning("V súbore neboli nájdené žiadne číselné stĺpce.")
        st.stop()

    if not categorical_columns:
        st.warning("V súbore neboli nájdené žiadne kategóriové stĺpce.")
        st.stop()

    st.subheader("Nastavenie analýzy")

    default_score = "leadership_score" if "leadership_score" in numeric_columns else numeric_columns[0]
    score_col = st.selectbox("Vyber analyzovaný ukazovateľ", options=numeric_columns, index=numeric_columns.index(default_score))

    default_group = "subor_povod" if "subor_povod" in categorical_columns else ("profesia_3g" if "profesia_3g" in categorical_columns else categorical_columns[0])
    group_col = st.selectbox("Vyber skupinovú premennú", options=categorical_columns, index=categorical_columns.index(default_group))

    if "profesia_3g" in df.columns:
        st.caption(
            "Poznámka: aplikácia automaticky vytvorila aj pomocný stĺpec 'profesia_3g' "
            "so skupinami Lekár, Sestra a Iné/Ostatné."
        )

    work_df = df[[group_col, score_col]].dropna().copy()
    unique_groups = list(work_df[group_col].unique())

    st.write(f"Počet skupín po odstránení chýbajúcich hodnôt: **{len(unique_groups)}**")
    st.write(f"Skupiny: **{', '.join(str(x) for x in unique_groups)}**")

    if st.button("Vykonať porovnanie skupín"):
        if len(unique_groups) < 2:
            st.error("Na porovnanie sú potrebné aspoň 2 skupiny.")
            st.stop()

        summary_df = group_summary(work_df, group_col, score_col)
        st.subheader("Deskriptívny prehľad skupín")
        st.dataframe(summary_df, use_container_width=True)

        results = {}

        if len(unique_groups) == 2:
            g1, g2 = unique_groups[0], unique_groups[1]
            vals1 = work_df.loc[work_df[group_col] == g1, score_col].dropna()
            vals2 = work_df.loc[work_df[group_col] == g2, score_col].dropna()

            stat, p_value = mannwhitneyu(vals1, vals2, alternative="two-sided")
            results = {
                "test": "Mann-Whitney U",
                "ukazovatel": score_col,
                "skupinova_premenna": group_col,
                "skupina_1": g1,
                "n_1": int(len(vals1)),
                "priemer_1": float(vals1.mean()),
                "median_1": float(vals1.median()),
                "skupina_2": g2,
                "n_2": int(len(vals2)),
                "priemer_2": float(vals2.mean()),
                "median_2": float(vals2.median()),
                "test_statistika": float(stat),
                "p_value": float(p_value),
            }
        else:
            group_values: List[pd.Series] = []
            for g in unique_groups:
                vals = work_df.loc[work_df[group_col] == g, score_col].dropna()
                if len(vals) > 0:
                    group_values.append(vals)

            stat, p_value = kruskal(*group_values)
            results = {
                "test": "Kruskal-Wallis",
                "ukazovatel": score_col,
                "skupinova_premenna": group_col,
                "pocet_skupin": int(len(unique_groups)),
                "test_statistika": float(stat),
                "p_value": float(p_value),
            }

        results_df = pd.DataFrame([results])

        st.subheader("Výsledok testu")
        st.dataframe(results_df, use_container_width=True)

        if results["p_value"] < 0.001:
            st.success("Výsledok je štatisticky významný na hladine p < 0,001.")
        elif results["p_value"] < 0.05:
            st.success(f"Výsledok je štatisticky významný (p = {results['p_value']:.4f}).")
        else:
            st.info(f"Rozdiel medzi skupinami sa štatisticky nepotvrdil (p = {results['p_value']:.4f}).")

        csv_buffer = io.StringIO()
        results_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="Stiahnuť výsledok testu ako CSV",
            data=csv_buffer.getvalue(),
            file_name="porovnanie_skupin_vysledok.csv",
            mime="text/csv",
        )

        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            summary_df.to_excel(writer, sheet_name="deskriptivne_skupiny", index=False)
            results_df.to_excel(writer, sheet_name="vysledok_testu", index=False)

        st.download_button(
            label="Stiahnuť výsledky ako XLSX",
            data=xlsx_buffer.getvalue(),
            file_name="porovnanie_skupin_vysledok.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
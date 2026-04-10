import sys

try:
    import pandas as pd
except ModuleNotFoundError:
    print(
        "Chýba balík 'pandas'. Nainštaluj ho priamo do Pythonu, ktorý používaš na spustenie:\n"
        f"  {sys.executable} -m pip install pandas streamlit openpyxl odfpy\n\n"
        "Tento súbor je Streamlit aplikácia a má sa spúšťať takto:\n"
        f"  {sys.executable} -m streamlit run {__file__}"
    )
    raise SystemExit(1)

try:
    import streamlit as st
except ModuleNotFoundError:
    print(
        "Chýba balík 'streamlit'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install streamlit\n\n"
        "Potom aplikáciu spusti takto:\n"
        f"  {sys.executable} -m streamlit run {__file__}"
    )
    raise SystemExit(1)

from typing import List
import io

if not getattr(st, "runtime", None) or not st.runtime.exists():
    print(
        "Toto je Streamlit aplikácia. Nespúšťaj ju cez obyčajné 'python'.\n"
        "Použi príkaz:\n"
        f"  {sys.executable} -m streamlit run {__file__}"
    )
    raise SystemExit(1)


st.set_page_config(page_title="Cronbach alfa", layout="wide")


def cronbach_alpha(df: pd.DataFrame) -> float:
    """
    Vypočíta Cronbachovu alfu pre DataFrame, kde:
    - riadky = respondenti
    - stĺpce = položky škály
    """
    df = df.dropna()

    k = df.shape[1]
    if k < 2:
        raise ValueError("Cronbachovu alfu nemožno vypočítať pre menej ako 2 položky.")

    item_variances = df.var(axis=0, ddof=1)
    total_score = df.sum(axis=1)
    total_variance = total_score.var(ddof=1)

    if total_variance == 0:
        raise ValueError("Celkové skóre má nulový rozptyl.")

    return float((k / (k - 1)) * (1 - item_variances.sum() / total_variance))


def load_data(uploaded_file) -> pd.DataFrame:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    if file_name.endswith(".ods"):
        return pd.read_excel(uploaded_file, engine="odf")

    raise ValueError("Podporované formáty sú: CSV, XLSX, ODS.")


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    numeric_cols: List[str] = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
    return numeric_cols


st.title("Výpočet Cronbachovej alfy")
st.write("Nahraj dátový súbor, vyber položky škály a aplikácia vypočíta Cronbachovu alfu.")

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

    st.subheader("Náhľad dát")
    st.dataframe(df.head(20), use_container_width=True)

    st.write(f"Počet riadkov: **{df.shape[0]}**")
    st.write(f"Počet stĺpcov: **{df.shape[1]}**")

    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        st.warning("V súbore neboli nájdené žiadne číselné stĺpce.")
        st.stop()

    st.subheader("Výber položiek škály")

    selected_columns = st.multiselect(
        "Vyber stĺpce, z ktorých chceš počítať Cronbachovu alfu",
        options=numeric_columns,
    )

    reverse_columns = st.multiselect(
        "Reverzne skórované položky (1–5)",
        options=selected_columns,
        help="Ak máš otázky typu 1 až 5, reverz sa počíta ako 6 - hodnota.",
    )

    if st.button("Vypočítať Cronbachovu alfu"):
        if len(selected_columns) < 2:
            st.warning("Vyber aspoň 2 položky.")
            st.stop()

        work_df = df[selected_columns].copy()

        for col in reverse_columns:
            work_df[col] = work_df[col].apply(
                lambda x: 6 - x if pd.notna(x) else x
            )

        try:
            alpha = cronbach_alpha(work_df)
        except Exception as e:
            st.error(f"Výpočet zlyhal: {e}")
            st.stop()

        st.success(f"Cronbachova alfa: {alpha:.3f}")

        st.subheader("Použitý dataset po výbere položiek")
        st.dataframe(work_df.head(20), use_container_width=True)

        st.subheader("Základné informácie")
        st.write(f"Počet položiek v škále: **{work_df.shape[1]}**")
        st.write(f"Počet kompletných respondentov použitých vo výpočte: **{len(work_df.dropna())}**")

        csv_buffer = io.StringIO()
        work_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="Stiahnuť použitý poddataset ako CSV",
            data=csv_buffer.getvalue(),
            file_name="cronbach_poddataset.csv",
            mime="text/csv",
        )
import streamlit as st

def vypocitaj_bsa(vaha, vyska):
    """Vypočíta telesný povrch (BSA) podľa vzorca DuBois."""
    return round(0.007184 * (vaha ** 0.425) * (vyska ** 0.725), 2)

def main():
    st.title("Predpis chemoterapie - Urotel GC Protokol")
    st.write("Aplikácia vypočíta dávky chemoterapie na základe protokolu Urotel GC.")

    # Vstupy pre váhu a výšku
    vaha = st.number_input("Zadajte hmotnosť (kg):", min_value=1.0, max_value=250.0, step=0.1, format="%.1f")
    vyska = st.number_input("Zadajte výšku (cm):", min_value=1.0, max_value=250.0, step=0.1, format="%.1f")

    if vaha > 0 and vyska > 0:
        # Výpočet BSA
        bsa = vypocitaj_bsa(vaha, vyska)
        st.write(f"**Vypočítaný telesný povrch (BSA):** {bsa} m²")

        # Dávka Gemcitabínu
        davka_gemcitabin = round(1000 * bsa, 2)
        st.write(f"**Dávka Gemcitabínu:** {davka_gemcitabin} mg na Dni 1 a 8")

        # Dávka Cisplatiny
        davka_cisplatina = round(70 * bsa, 2)
        st.write(f"**Dávka Cisplatiny:** {davka_cisplatina} mg na Deň 1")

        # Hydratácia a premedikácia
        st.subheader("Hydratácia a premedikácia:")
        st.write("""
        - **Deň 0:**
            - 1000 ml FR 1/1 i.v.
            - 500 ml 10% Manitol i.v.
            - 500 ml FR 1/1 i.v. + 10 ml KCl 7,5% + 5 ml MgSO4 20%
        - **Deň 1:**
            - Omeprazol 20 mg tbl (1-0-0)
            - Aprepitant 125 mg (1-0-0)
            - 12 mg Dexametazón i.v.
            - 1 ampulka Granisetron i.v.
            - 250 ml FR 1/1 i.v. + Gemcitabín
            - 500 ml FR 1/1 i.v. + Cisplatina
            - 500 ml Manitol 10%
        """)

if __name__ == "__main__":
    main()
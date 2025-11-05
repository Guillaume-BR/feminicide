import streamlit as st
from utils.functions import load_global_css

load_global_css()


st.title("📚 Autres ressources")

st.write("Pour en savoir plus sur le sujet des féminicides, voici quelques ressources supplémentaires :")
st.markdown("""
- Merci au collectif NousToutes : [https://www.noustoutes.org/](https://www.noustoutes.org/).
    N'hésitez pas à participer à leur [enquête](https://www.noustoutes.org/enquetes/)
- Fondation des Femmes : [https://www.fondationdesfemmes.org/](https://www.fondationdesfemmes.org/)
- Observatoire des Violences Faites aux Femmes en Hérault : [https://www.ovff34.fr/](https://www.ovff34.fr/)
- Haut Conseil à l'Égalité entre les femmes et les hommes (HCE) sur les féminicides : [https://www.haut-conseil-egalite.gouv.fr/](https://www.haut-conseil-egalite.gouv.fr/)
- Site sur les féminicides en France : [https://feminicides.fr/](https://feminicides.fr/)
- Livre de Mona Chollet "Sorcières : La puissance invaincue des femmes" : [Sorcières : La puissance invaincue des femmes](https://www.editionsladecouverte.fr/sorcieres_la_puissance_invaincue_des_femmes-9782355221224)
- Livre de Noémie Renard "En finir avec la culture du viol" : [En finir avec la culture du viol](https://www.lespetitsmatins.fr/collections/essais/213-en-finir-avec-la-culture-du-viol.html)   """)

st.write("N'hésitez pas à consulter ces ressources pour obtenir des informations, du soutien et des moyens d'agir contre les violences faites aux femmes.")

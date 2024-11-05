import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Exibindo uma imagem no cabeçalho
st.image("logo.png", use_column_width=True)  # Altere para o caminho da imagem ou URL
st.title("Análise Estrutural de uma Ponte")
st.caption("Ferramenta interativa para análise de carga distribuída e reações de apoio.")
st.caption("Desenvolvido em Python pela Profa. Adriana Regina Tozzi para a Disciplina de Pontes do Curso de Engenharia Civil do Centro Universitário Uninter.")

# Parâmetros ajustáveis na interface
comprimento_ponte = st.number_input("Comprimento total da ponte (m)", value=100)
carga_distribuida = st.number_input("Carga distribuída (kN/m)", value=20)
posicoes_vigas = st.text_input("Posições das vigas de sustentação (em metros, separadas por vírgulas)", value="0,25,50,75,100")
num_longarinas = st.number_input("Número de Longarinas", min_value=1, value=5)  # Número de longarinas

# Botão de recalcular
if st.button("Recalcular"):
    # Conversão das posições das vigas para uma lista de inteiros
    posicoes_vigas = [float(pos) for pos in posicoes_vigas.split(',')]
    n_vigas = len(posicoes_vigas)  # Número de vigas de sustentação

    # Calculando a carga total e dividindo entre as longarinas
    carga_total = carga_distribuida * comprimento_ponte
    carga_por_longarina = carga_total / num_longarinas  # Dividindo a carga total entre as longarinas

    # Supondo uma distribuição de carga proporcional à distância entre vigas
    distancias_entre_vigas = np.diff(posicoes_vigas)  # Distâncias entre vigas
    pesos_por_viga = (distancias_entre_vigas / comprimento_ponte) * carga_total  # Carga suportada por cada viga

    # Calculando as reações de apoio (aproximadas) nas vigas
    reacoes = np.zeros(n_vigas)
    reacoes[1:-1] = (pesos_por_viga[:-1] + pesos_por_viga[1:]) / 2  # Vigas intermediárias
    reacoes[0] = pesos_por_viga[0] / 2  # Primeira viga
    reacoes[-1] = pesos_por_viga[-1] / 2  # Última viga

    # Definindo pontos ao longo do comprimento da ponte para calcular a força cortante e o momento fletor
    x_pontos = np.linspace(0, comprimento_ponte, 500)
    forca_cortante_total = np.zeros_like(x_pontos)
    momento_fletor_total = np.zeros_like(x_pontos)

    # Calculando a força cortante e o momento fletor em cada ponto
    for i, x in enumerate(x_pontos):
        # Contribuição das reações de apoio para força cortante e momento
        for j, posicao_viga in enumerate(posicoes_vigas):
            if x >= posicao_viga:
                forca_cortante_total[i] += reacoes[j]
                momento_fletor_total[i] += reacoes[j] * (x - posicao_viga)
        # Subtraindo a contribuição da carga distribuída
        forca_cortante_total[i] -= carga_distribuida * x
        momento_fletor_total[i] -= carga_distribuida * x * (x / 2)  # Integrando a carga distribuída até o ponto x

    # Dividindo os resultados para cada longarina
    forca_cortante_por_longarina = forca_cortante_total / num_longarinas
    momento_fletor_por_longarina = momento_fletor_total / num_longarinas

    # Plotando o diagrama de corpo livre, momento fletor e força cortante totais
    fig, axs = plt.subplots(3, 1, figsize=(12, 12))

    # Subplot do diagrama de corpo livre
    axs[0].plot([0, comprimento_ponte], [0, 0], color="gray", linewidth=4, label="Ponte")
    axs[0].scatter(posicoes_vigas, np.zeros(n_vigas), color="blue", s=100, zorder=5, label="Vigas de Sustentação")
    axs[0].vlines(posicoes_vigas, 0, reacoes, colors="red", linestyles="dashed", label="Reações de Apoio")
    axs[0].bar(posicoes_vigas, reacoes, width=1, color="red", alpha=0.5)
    axs[0].plot(np.linspace(0, comprimento_ponte, 500), np.ones(500) * carga_distribuida, color="green", linewidth=2, label="Carga Distribuída")
    axs[0].set_title("Diagrama de Corpo Livre com Reações de Apoio e Carga Distribuída")
    axs[0].set_xlabel("Comprimento da Ponte (m)")
    axs[0].set_ylabel("Força (kN)")
    axs[0].legend()
    axs[0].grid(True)

    # Subplot do diagrama de força cortante total
    axs[1].plot(x_pontos, forca_cortante_total, color="orange", label="Força Cortante Total")
    axs[1].fill_between(x_pontos, forca_cortante_total, color="orange", alpha=0.3)
    axs[1].set_title("Diagrama de Força Cortante Total ao Longo da Ponte")
    axs[1].set_xlabel("Comprimento da Ponte (m)")
    axs[1].set_ylabel("Força Cortante (kN)")
    axs[1].legend()
    axs[1].grid(True)

    # Subplot do diagrama de momento fletor total
    axs[2].plot(x_pontos, momento_fletor_total, color="purple", label="Momento Fletor Total")
    axs[2].fill_between(x_pontos, momento_fletor_total, color="purple", alpha=0.3)
    axs[2].set_title("Diagrama de Momento Fletor Total ao Longo da Ponte")
    axs[2].set_xlabel("Comprimento da Ponte (m)")
    axs[2].set_ylabel("Momento Fletor (kN·m)")
    axs[2].legend()
    axs[2].grid(True)

    # Exibindo o gráfico na aplicação Streamlit para o total
    plt.tight_layout()
    st.pyplot(fig)

    # Plotando os gráficos para cada longarina individualmente
    st.subheader(f"Diagrama para cada Longarina")

    fig_longarina, axs_longarina = plt.subplots(2, 1, figsize=(10, 8))

    # Diagrama de Força Cortante para a Longarina
    axs_longarina[0].plot(x_pontos, forca_cortante_por_longarina, color="orange", label="Força Cortante")
    axs_longarina[0].fill_between(x_pontos, forca_cortante_por_longarina, color="orange", alpha=0.3)
    axs_longarina[0].set_title(f"Força Cortante - Longarina")
    axs_longarina[0].set_xlabel("Comprimento da Ponte (m)")
    axs_longarina[0].set_ylabel("Força Cortante (kN)")
    axs_longarina[0].legend()
    axs_longarina[0].grid(True)

    # Diagrama de Momento Fletor para a Longarina
    axs_longarina[1].plot(x_pontos, momento_fletor_por_longarina, color="purple", label="Momento Fletor")
    axs_longarina[1].fill_between(x_pontos, momento_fletor_por_longarina, color="purple", alpha=0.3)
    axs_longarina[1].set_title(f"Momento Fletor - Longarina")
    axs_longarina[1].set_xlabel("Comprimento da Ponte (m)")
    axs_longarina[1].set_ylabel("Momento Fletor (kN·m)")
    axs_longarina[1].legend()
    axs_longarina[1].grid(True)

    # Exibindo o gráfico na aplicação Streamlit para cada longarina
    plt.tight_layout()
    st.pyplot(fig_longarina)

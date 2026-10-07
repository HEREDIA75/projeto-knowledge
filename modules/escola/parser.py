import io
from typing import Any, Dict, List
import pandas as pd


def converter_nota_para_float(valor: Any) -> float:
    """Converte valores com segurança para float, tratando 'S/N', '-', etc."""
    if pd.isna(valor) or valor is None:
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    val_str = str(valor).strip().replace(",", ".")

    if val_str.upper() in ["S/N", "SN", "-", "ND", "N/A", ""]:
        return 0.0

    try:
        return float(val_str)
    except ValueError:
        return 0.0


def processar_planilha_replanejamento(
    file_path_or_bytes,
) -> List[Dict[str, Any]]:
    """Processa planilhas de disciplinas e Mapões de conselho."""
    xls = pd.ExcelFile(file_path_or_bytes)
    registros_consolidados = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # 1. Disciplinas Técnicas
        if "Nome" in df.columns and "Média" in df.columns:
            for _, row in df.iterrows():
                nome = row.get("Nome")
                if pd.isna(nome) or str(nome).strip() == "":
                    continue

                registros_consolidados.append(
                    {
                        "tipo_documento": "DISCIPLINA_TECNICA",
                        "aba_disciplina": sheet_name.strip(),
                        "numero": (
                            int(row.get("N°"))
                            if pd.notna(row.get("N°")) and str(row.get("N°")).isdigit()
                            else None
                        ),
                        "situacao": str(row.get("Situação", "Ativo")).strip(),
                        "nome_aluno": str(nome).strip(),
                        "trabalho": converter_nota_para_float(row.get("Trabalho")),
                        "atividades": converter_nota_para_float(row.get("Atividades")),
                        "prova": converter_nota_para_float(row.get("Prova")),
                        "prova_paulista": converter_nota_para_float(
                            row.get("Prova Paulista")
                        ),
                        "media_final": converter_nota_para_float(row.get("Média")),
                    }
                )

        # 2. Mapão de Conselho
        elif "ALUNO" in df.columns:
            df_alunos = df.dropna(subset=["ALUNO"])

            for _, row in df_alunos.iterrows():
                aluno_nome = row.get("ALUNO")
                if pd.isna(aluno_nome) or str(aluno_nome).strip() == "":
                    continue

                registros_consolidados.append(
                    {
                        "tipo_documento": "MAPAO_CONSELHO",
                        "bimestre": sheet_name.strip(),
                        "nome_aluno": str(aluno_nome).strip(),
                        "situacao": str(row.get("SITUAÇÃO", "Ativo")).strip(),
                        "faltas_totais": converter_nota_para_float(row.get("TF")),
                        "frequencia_pct": str(row.get("Fre(%)", "100%")).strip(),
                    }
                )

    return registros_consolidados

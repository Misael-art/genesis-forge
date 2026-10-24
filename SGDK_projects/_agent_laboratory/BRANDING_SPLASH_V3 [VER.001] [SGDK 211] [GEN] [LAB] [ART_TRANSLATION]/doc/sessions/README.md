# Documentos de sessao

Cada sessao de trabalho relevante (diagnostico, laboratorio, integracao) gera um `.md`
datado no nome (`AAAA_MM_DD`, `AAAAMMDD` ou `AAAA-MM-DD`) nesta pasta.

Toda sessao precisa de entrada no memory bank (`doc/10-memory-bank.md`) citando o nome
do arquivo. O auditor reprova sessao sem entrada:

```bash
python3 ../../tools/sgdk_wrapper/audit_session_backfill.py --project "$PWD" --ref HEAD
```

`--ref HEAD` audita o memory bank commitado: backfill so na arvore de trabalho nao conta.

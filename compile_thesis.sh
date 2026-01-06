#!/bin/bash
# Script to compile the thesis LaTeX document

echo "Compiling thesis document..."
export PATH="/usr/local/texlive/2025basic/bin/universal-darwin:$PATH"
pdflatex tesis_text_to_sql.tex
pdflatex tesis_text_to_sql.tex  # Second pass for cross-references

echo "✅ Compilation complete! Opening PDF..."
open tesis_text_to_sql.pdf
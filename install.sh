#!/bin/bash
{
    pip install -r requirements.txt
} || {
    echo "Erro durante a instalação das dependências" > install_error.log
    exit 1
}

:: version: '1.0.0'
:: rev date:
:: author: Will Morris
:: created date: 11/10/2026
:: usage: .cmd
:: purpose:

@echo off
setlocal

set path_arg=%1

dt rpr %path_arg% --md --file ./docs/%path_arg%.md

endlocal

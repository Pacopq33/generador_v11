```nsis
; generador-titulos-vt.nsi
!include MUI2.nsh
!include LogicLib.nsh

; Configuración general
!define MUI_PRODUCT "generador-titulos-utn"
!define MUI_VERSION "1.0"
!define MUI_PUBLISHER "Fede-UTN" ; Cambia por tu nombre o empresa
OutFile "generador-titulos-vt_Setup.exe"
InstallDir "C:\Archivos de Programa\generador-titulos-utn"
RequestExecutionLevel admin

; Páginas de Modern UI
!define MUI_WELCOMEPAGE
!define MUI_DIRECTORYPAGE
!define MUI_FINISHPAGE
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
Page custom MikTeXPage MikTeXPageLeave
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "Spanish"

; Variables
Var MikTeXPath

; Página personalizada para la ruta de MiKTeX
Function MikTeXPage
  !insertmacro MUI_HEADER_TEXT "Ruta de MiKTeX" "Especifique la carpeta donde está pdflatex.exe (MiKTeX)"
  nsDialogs::Create 1018
  Pop $0
  ${NSD_CreateLabel} 0 0 100% 24u "Seleccione la carpeta que contiene pdflatex.exe (MiKTeX):"
  Pop $0
  ${NSD_CreateDirRequest} 0 30u 75% 12u "$PROGRAMFILES\MiKTeX 2.9\miktex\bin\x64"
  Pop $MikTeXPath
  ${NSD_CreateBrowseButton} 75% 30u 25% 12u "Examinar..."
  Pop $1
  ${NSD_OnClick} $1 BrowseMikTeX
  nsDialogs::Show
FunctionEnd

Function BrowseMikTeX
  nsDialogs::SelectFolderDialog "Seleccione la carpeta de MiKTeX" "$PROGRAMFILES\MiKTeX 2.9"
  Pop $0
  ${If} $0 != error
    ${NSD_SetText} $MikTeXPath $0
  ${EndIf}
FunctionEnd

Function MikTeXPageLeave
  ${NSD_GetText} $MikTeXPath $MikTeXPath
  IfFileExists "$MikTeXPath\pdflatex.exe" 0 MikTeXNotFound
    ; Verificar pdflatex ejecutando pdflatex --version
    nsExec::ExecToStack '"$MikTeXPath\pdflatex.exe" --version'
    Pop $0
    Pop $1
    ${If} $0 == 0
      ; Añadir al PATH del sistema
      ReadRegStr $2 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
      StrCpy $3 "$2;$MikTeXPath"
      WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" "$3"
      Goto Done
    ${Else}
      Goto MikTeXNotFound
    ${EndIf}
  MikTeXNotFound:
    MessageBox MB_OK|MB_ICONEXCLAMATION "MiKTeX no encontrado en la ruta especificada. Por favor, descargue e instale MiKTeX desde https://miktex.org/ y especifique la ruta correcta."
    Abort
  Done:
FunctionEnd

; Verificación de Windows 10 o superior
Function .onInit
  ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" "CurrentVersion"
  ${If} $0 < 6.2
    MessageBox MB_OK|MB_ICONEXCLAMATION "Este programa requiere Windows 10 o superior."
    Abort
  ${EndIf}
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\generador-titulos-vt\*"
  CreateShortCut "$DESKTOP\GeneradorTitulos.lnk" "$INSTDIR\generador-titulos-vt.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  Delete "$DESKTOP\GeneradorTitulos.lnk"
SectionEnd
```
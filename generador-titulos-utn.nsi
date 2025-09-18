; generador-titulos-utn.nsi
!include MUI2.nsh

!define MUI_PRODUCT "generador-titulos-utn"
!define MUI_VERSION "1.1"
!define MUI_PUBLISHER "Fede-UTN"

OutFile "generador-titulos-utn_Setup.exe"
InstallDir "C:\\Archivos de Programa\\generador-titulos-utn"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "Spanish"

Function .onInit
  ReadRegStr $0 HKLM "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" "CurrentVersion"
  ${If} $0 < 6.2
    MessageBox MB_OK|MB_ICONEXCLAMATION "Este programa requiere Windows 10 o superior."
    Abort
  ${EndIf}
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\\generador-titulos-vt\\*"
  CreateShortCut "$DESKTOP\\GeneradorTitulos.lnk" "$INSTDIR\\generador-titulos-vt.exe"
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\*.*"
  RMDir /r "$INSTDIR"
  Delete "$DESKTOP\\GeneradorTitulos.lnk"
SectionEnd

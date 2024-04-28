Private Sub CommandButton1_Click()
    Dim openFileDialog As FileDialog

    ' 파일 선택 대화 상자 생성
    Set openFileDialog = Application.FileDialog(msoFileDialogFilePicker)

    ' 파일 선택 대화 상자 설정
    With openFileDialog
        .Title = "파일 선택"
        .Filters.Clear
        .Filters.Add "텍스트 파일", "*.txt"
        .AllowMultiSelect = False ' 단일 파일 선택만 허용
        .InitialFileName = "C:\Users\CKIRUser\Downloads\" ' 초기 디렉토리 설정
        If .Show = -1 Then ' 사용자가 "열기"를 선택하면
            ' 선택한 파일의 경로 설정
            ThisWorkbook.Sheets("Sheet1").Range("I4").Value = .SelectedItems(1)
        Else
            ' 사용자가 취소를 선택한 경우
            MsgBox "파일 선택이 취소되었습니다.", vbInformation
            Exit Sub
        End If
    End With
End Sub

Private Sub ComboBox1_Change()
    Dim filePath As String
    Dim fileContent As String
    Dim lines() As String
    Dim selectedItem As String
    Dim i As Integer
    Dim j As Integer
    Dim output As String
    Dim foundItem As Boolean

    ' 이전 출력 지우기
    Range("D8").Value = ""

    ' 선택한 파일의 경로 가져오기
    filePath = ThisWorkbook.Sheets("Sheet1").Range("I4").Value

    ' ComboBox1에서 선택된 항목 가져오기
    selectedItem = ComboBox1.Value

    On Error Resume Next
    ' 파일 내용 읽기
    Open filePath For Input As #1
    If Err.Number <> 0 Then
        MsgBox "파일을 열 수 없습니다: " & filePath, vbExclamation
        Exit Sub
    End If
    fileContent = Input$(LOF(1), 1)
    Close #1
    On Error GoTo 0

    ' 파일 내용을 줄 단위로 분할
    lines = Split(fileContent, vbCrLf)

    ' 선택된 항목과 일치하는 줄 찾기
    For i = LBound(lines) To UBound(lines)
        If InStr(1, lines(i), selectedItem) > 0 Then
            foundItem = True
            ' 선택된 항목이 포함된 줄 찾으면 해당 항목 및 다음 줄들을 가져와 출력
            If Left(lines(i), 4) = "URL:" Then
                ' URL 키워드를 찾으면 해당 줄부터 출력
                output = output & lines(i) & vbCrLf
                For j = i + 1 To UBound(lines)
                    output = output & lines(j) & vbCrLf
                    If Left(lines(j), 1) = "=" Then ' 구분선인 경우 출력 종료
                        Exit For
                    End If
                Next j
            End If
        End If
    Next i

    ' 선택된 항목이 없을 경우 메시지 출력
    If Not foundItem Then
        output = "해당 항목을 찾을 수 없습니다."
    End If

    ' 결과를 D8에 표시
    Range("D8").Value = output
End Sub

Private Sub Worksheet_Activate()
    ' ComboBox1 채우기
    ComboBox1.List = Array("alba", "a-bly", "afreeca", "flybit")
End Sub

Private Sub ComboBox1_Change()
    Dim filePath As String
    Dim fileContent As String
    Dim lines() As String
    Dim selectedItem As String
    Dim i As Integer
    Dim output As String
    Dim foundItem As Boolean

    ' ComboBox1에서 선택한 항목 가져오기
    selectedItem = ComboBox1.Value

    ' 파일 경로 설정
    filePath = "C:\Users\CKIRUser\Downloads\Passwords.txt"

    ' 파일 내용 읽기
    Open filePath For Input As #1
    fileContent = Input$(LOF(1), 1)
    Close #1

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

    ' 결과를 B5에 표시
    Range("D8").Value = output
End Sub


Private Sub Worksheet_Activate()
    ' ComboBox1 채우기
    ComboBox1.List = Array("alba", "a-bly", "afreeca", "flybit")
    ' ComboBox1 변경 이벤트 발생
    ComboBox1_Change
End Sub



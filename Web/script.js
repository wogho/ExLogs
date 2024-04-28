document.addEventListener('DOMContentLoaded', function() {
    var fileInput = document.getElementById('fileInput');
    var comboBox = document.getElementById('comboBox');
    var fileContent = document.getElementById('fileContent');

    fileInput.addEventListener('change', function(event) {
        var selectedFile = event.target.files[0];
        var reader = new FileReader();

        reader.onload = function(event) {
            fileContent.textContent = event.target.result;
        };

        reader.readAsText(selectedFile);
    });

    comboBox.addEventListener('change', function() {
        var selectedOption = comboBox.value;
        var filePath = "C:\\Users\\CKIRUser\\Downloads\\" + selectedOption + ".txt"; // 파일 경로 수정 필요
        fileInput.value = ''; // 파일 선택 input 초기화

        // 파일 이름 표시
        fileContent.textContent = "선택된 파일: " + filePath;
    });
});

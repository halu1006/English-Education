$(document).ready(function() {
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    $("#recordButton").click(function() {
        if (!isRecording) {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        $("#audioPlayback").attr("src", audioUrl);

                        const formData = new FormData();
                        formData.append('audio', audioBlob, 'recording.webm');

                        $.ajax({
                            url: '/transcribe',
                            type: 'POST',
                            data: formData,
                            processData: false,
                            contentType: false,
                            success: function(response) {
                                $("#transcription").text(response.text);

                                // 正誤判定をサーバーに問い合わせ、結果を動的に表示
                                $.ajax({
                                    url: '/judge',
                                    type: 'POST',
                                    data: {
                                        input_text: $("textarea[name='input_text']").val(),
                                        transcription_text: response.text,
                                        pos_checkbox: $("input[name='pos_checkbox']:checked").map(function() {
                                            return this.value;
                                        }).get()
                                    },
                                    success: function(data) {
                                        // 正誤判定結果を表示
                                        $("#judgeResult").html(data.is_correct ?
                                            '<p style="color: green;">正解</p>' :
                                            '<p style="color: red;">不正解</p>');
                                    },
                                    error: function(error) {
                                        console.error("正誤判定エラー:", error);
                                        $("#judgeResult").text("正誤判定中にエラーが発生しました");
                                    }
                                });
                            },
                            error: function(error) {
                                console.error("Transcription error:", error);
                                $("#transcription").text("エラーが発生しました");
                            }
                        });

                        audioChunks = [];
                        isRecording = false;
                    };

                    mediaRecorder.start();
                    isRecording = true;
                    $("#recordButton").text("録音停止");
                })
                .catch(error => {
                    console.error("Error accessing microphone:", error);
                    $("#transcription").text("マイクへのアクセスエラー");
                });
        } else {
            mediaRecorder.stop();
            $("#recordButton").text("録音開始");
        }
    });
});
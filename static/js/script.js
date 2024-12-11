// $(document).ready(function () {

//     function hideElement() {
//       var element = document.querySelector('.suggestbox');
//       element.classList.add('hidden'); // Add the 'hidden' class to hide the element
//     }

//     function showElement() {
//       var element = document.querySelector('.suggestbox');
//       element.classList.remove('hidden'); // Remove the 'hidden' class to show the element
//     }
    
//     function typeWriter(text, index, messageContainer) {
//       if (index < text.length) {
//         messageContainer.append(text.charAt(index));
//         index++;
//         setTimeout(function () {
//           typeWriter(text, index, messageContainer);
//         }, 30); // Adjust typing speed (in milliseconds) here
//       }
//     }


//     const inputBox = document.getElementById("text");
//     inputBox.addEventListener("input", function () {
//       const inputValue = inputBox.value;
      
//       // Make an HTTP request to /recommend
//       fetch("/recommend", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ inputValue: inputValue }),
//       })
//         .then((response) => response.json())
//         .then((data) => {
//           // Initialize all buttons to be hidden
//           for (var i = 1; i <= 5; i++) {
//             var recommendId = "#recommend_" + i;
//             var button = document.getElementById("recommend_" + i);

//             // Hide the button
//             if (button || button.textContent.trim() !== "") {
//                 button.style.display = "none";
//             }
//         }

//         // Display buttons with non-empty content
//         for (var i = 1; i <= 5; i++) {
//             var recommendId = "#recommend_" + i;
//             var button = document.getElementById("recommend_" + i);

//             // Set text content
//             $(recommendId).text(data["recommend_" + i]);

//             // Display the button if the content is not empty
//             if (button && button.textContent.trim() !== "") {
//                 button.style.display = "inline-block"; 
//             }
//         }
//         })
//         .catch((error) => {
//           console.error("Error:", error);
//         });
//     });

//       const recommendButtons = document.querySelectorAll(".suggestbox");
//       const textInput = document.getElementById("text");

//       recommendButtons.forEach(function(button) {
//         button.addEventListener("click", function() {
//           const buttonText = button.textContent;
//           textInput.value = buttonText;
//         });
//       });

//     $("#messageArea").on("submit", function (event) {
//       event.preventDefault();
        
//       const date = new Date();
//       const hour = date.getHours();
//       const minute = date.getMinutes();
//       const str_time = hour + ":" + minute;
//       var rawText = $("#text").val();

//       var userHtml =
//         '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' +
//         rawText +
//         '<span class="msg_time_send">' +
//         str_time +
//         '</span></div><div class="img_cont_msg"><img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg"></div></div>';

//       $("#text").val("");
//       $("#messageFormeight").append(userHtml);

//       // 加入等待動畫
//       var loadingHtml =
//         '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg_wait"><img src="https://d1fdloi71mui9q.cloudfront.net/hpjl93k9TaGKATsY5cnB_Zh02MiHnXpM88o10" class="rounded-circle user_img_msg"></div><div class="msg_cotainer_wait"><img src="./static/loading.gif" style="width:100px;height:50px"></div></div>';
//       $("#messageFormeight").append(loadingHtml);
      
//       $.ajax({
//         data: {
//           msg: rawText,
//         },
//         type: "POST",
//         url: "/get",
//       })
//         .done(function (data) {
//           // 移除等待動畫
//           $(".msg_cotainer_wait").hide().remove();
//           $(".img_cont_msg_wait").hide().remove();

//           function displayBotResponse(data) {
//             var botHtml =
//               '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="https://d1fdloi71mui9q.cloudfront.net/hpjl93k9TaGKATsY5cnB_Zh02MiHnXpM88o10" class="rounded-circle user_img_msg"></div><div class="msg_cotainer"><span class="bot-response"></span></div></div>';

//             $("#messageFormeight").append($.parseHTML(botHtml));

//             var messageContainer = $("#messageFormeight")
//               .find(".bot-response")
//               .last(); // 取得最後新增的回覆標籤

//             setTimeout(function () {
//               typeWriter(data, 0, messageContainer);
//             }, 500); // Add a short delay before starting the typewriter effect
//           }
//           displayBotResponse(data);
//         })
//         .fail(function (xhr, status, error) {
//           console.log("AJAX請求發生錯誤:", error);
//         });

//       updateRecommendations();
//     });

    
//   });

$(document).ready(function () {

    function hideElement() {
        var element = document.querySelector('.suggestbox');
        element.classList.add('hidden'); // Add the 'hidden' class to hide the element
    }

    function showElement() {
        var element = document.querySelector('.suggestbox');
        element.classList.remove('hidden'); // Remove the 'hidden' class to show the element
    }
    
    function typeWriter(text, index, messageContainer) {
        if (index < text.length) {
        messageContainer.append(text.charAt(index));
        index++;
        setTimeout(function () {
            typeWriter(text, index, messageContainer);
        }, 30); // Adjust typing speed (in milliseconds) here
        }
    }

    const inputBox = document.getElementById("text");

    const recommendButtons = document.querySelectorAll(".suggestbox");
    const textInput = document.getElementById("text");

    recommendButtons.forEach(function(button) {
        button.addEventListener("click", function() {
            const buttonText = button.textContent;
            textInput.value = buttonText;
        });
    });

    $("#messageArea").on("submit", function (event) {
        event.preventDefault();
        
        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour + ":" + minute;
        var rawText = $("#text").val();

        var userHtml =
            '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' +
            rawText +
            '<span class="msg_time_send">' +
            str_time +
            '</span></div><div class="img_cont_msg"><img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg"></div></div>';

        $("#text").val("");
        $("#messageFormeight").append(userHtml);

        // 加入等待動畫
        var loadingHtml =
            '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg_wait"><img src="https://d1fdloi71mui9q.cloudfront.net/hpjl93k9TaGKATsY5cnB_Zh02MiHnXpM88o10" class="rounded-circle user_img_msg"></div><div class="msg_cotainer_wait"><img src="./static/loading.gif" style="width:100px;height:50px"></div></div>';
        $("#messageFormeight").append(loadingHtml);
        
        $.ajax({
            data: {
                msg: rawText,
            },
            type: "POST",
            url: "/get",
        })
        .done(function (data) {
            // 移除等待動畫
            $(".msg_cotainer_wait").hide().remove();
            $(".img_cont_msg_wait").hide().remove();

            function displayBotResponse(data) {
                var botHtml =
                    '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="https://d1fdloi71mui9q.cloudfront.net/hpjl93k9TaGKATsY5cnB_Zh02MiHnXpM88o10" class="rounded-circle user_img_msg"></div><div class="msg_cotainer"><span class="bot-response"></span></div></div>';

                $("#messageFormeight").append($.parseHTML(botHtml));

                var messageContainer = $("#messageFormeight")
                    .find(".bot-response")
                    .last(); // 取得最後新增的回覆標籤

                setTimeout(function () {
                    typeWriter(data, 0, messageContainer);
                }, 500); // Add a short delay before starting the typewriter effect
            }
            displayBotResponse(data);
            updateRecommendations();
        })
        .fail(function (xhr, status, error) {
            console.log("AJAX請求發生錯誤:", error);
        });
    });

    function updateRecommendations() {
        const inputValue = inputBox.value;

        // Make an HTTP request to /recommend
        fetch("/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ inputValue: inputValue }),
        })
        .then((response) => response.json())
        .then((data) => {
            // Initialize all buttons to be hidden
            for (var i = 1; i <= 5; i++) {
                var button = document.getElementById("recommend_" + i);

                // Hide the button
                if (button || button.textContent.trim() !== "") {
                    button.style.display = "none";
                }
            }

            // Display buttons with non-empty content
            for (var i = 1; i <= 5; i++) {
                var button = document.getElementById("recommend_" + i);

                // Set text content
                $(button).text(data["recommend_" + i]);

                // Display the button if the content is not empty
                if (button && button.textContent.trim() !== "") {
                    button.style.display = "inline-block"; 
                }
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    }
    });

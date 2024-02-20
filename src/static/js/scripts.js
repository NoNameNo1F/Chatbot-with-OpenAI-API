const lightModeToggle = document.getElementById("light-mode-toggle");
let isDarkMode = false;

lightModeToggle.addEventListener("click", () => {
  isDarkMode = !isDarkMode;

  if (isDarkMode) {
    document.body.style.backgroundColor = "#0c001f";
  } else {
    document.body.style.backgroundColor = "#e4d9f5";
  }
});
// Function to display modal when OpenAI Key link is clicked
document.getElementById("openAIKeyLink").addEventListener("click", function () {
  $("#openAIKeyModal").modal("show");
});

// Function to save OpenAI Key to localStorage
function sendAndSaveOpenAIKey() {
  var openAIKey = document.getElementById("openAIKeyInput").value;

  fetch("/api/openAIKeyInput", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      key: openAIKey,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var status = data.status;
      if (status === true) {
        localStorage.setItem("openAIKey", openAIKey);
        document.getElementById("keyStatus").className = "d-none";
        document.getElementById("keyStatus").innerHTML = "Ok";
        $("#openAIKeyModal").modal("hide");
      } else {
        document.getElementById("keyStatus").className = "d-inline";
        document.getElementById("keyStatus").innerHTML =
          "Invalid OpenAI API Key";
      }
    });
}

// Dictionary to store thread ids and their respective chat history
var threadChatHistory = {};
var activeThread = "";

// Retrieve stored chat history from local storage
function loadChatHistory() {
  var storedData = localStorage.getItem("threadChatHistory");
  if (storedData) {
    threadChatHistory = JSON.parse(storedData);
  }
}

// Save chat history to local storage
function saveChatHistory() {
  localStorage.setItem("threadChatHistory", JSON.stringify(threadChatHistory));
}

function switchThread(threadId) {
  // Load chat messages for the selected thread
  displayChatHistory(threadId);

  // Update the activeThread
  activeThread = threadId;
  fetch("/api/getUuid", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      uuid: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var uuid = data.uuid;
      history.pushState({}, "", "/thread/" + uuid);
    });
}

// Function to display chat history
function displayChatHistory(threadId) {
  var messages = threadChatHistory[threadId] || [];
  var messageContainer = document.getElementById("messageContainer");
  messageContainer.innerHTML = ""; // Clear existing messages

  messages.forEach(function (message) {
    var messageElement = document.createElement("div");
    messageElement.className =
      message.role === "user" ? "user-message" : "response-message";
    messageElement.innerText = message.content;

    messageContainer.appendChild(messageElement);
  });
}

function sendMessage() {
  var status = document.getElementById("keyStatus").innerHTML;
  if (status !== "Ok") {
    $("#openAIKeyModal").modal("show");
    return;
  }

  var userMessage = document.getElementById("messageInput").value;
  if (userMessage === "") {
    return;
  }

  // Create a user message element
  var userMessageElement = document.createElement("div");
  userMessageElement.className = "user-message";
  userMessageElement.innerText = userMessage;

  // Append the user message to the message container
  document.getElementById("messageContainer").appendChild(userMessageElement);

  // Make a POST request to the server
  fetch("/api", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: userMessage,
      thread_id: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var responseMessageElement = document.createElement("div");
      responseMessageElement.className = "response-message";
      responseMessageElement.innerText = data.message;

      document
        .getElementById("messageContainer")
        .appendChild(responseMessageElement);

      // Update the chat history for the active thread
      threadChatHistory[activeThread] = data.chat_history;

      // Save chat history to local storage
      saveChatHistory();
    });

  document.getElementById("messageInput").value = "";
}

// Function to create a new thread
function createNewThread() {
  var newThreadId = "thread" + (Object.keys(threadChatHistory).length + 1);

  // Create a new entry in the threadChatHistory dictionary
  threadChatHistory[newThreadId] = [];

  var listItem = document.createElement("li");
  listItem.className = "list-group-item p-3";
  listItem.innerText = "New Thread " + Object.keys(threadChatHistory).length;
  listItem.onclick = function () {
    switchThread(newThreadId);
  };

  document.getElementById("threadList").appendChild(listItem);

  // Switch to the new thread
  switchThread(newThreadId);
}

loadChatHistory();

// Load thread ID from the URL when the page is loaded
// window.onload = function () {
//   var url = window.location.href;
//   var threadIdMatch = url.match(/\/thread\/(\w+)/);
//   if (threadIdMatch) {
//     var threadId = threadIdMatch[1];
//     switchThread(threadId);
//   }
// };

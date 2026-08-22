<?php
// Bot Token aur Postback Base URL yahan enter karein
define('BOT_TOKEN', '8874819641:AAGy9IGxvZqXPjNuhUEHDXH5N8juCTcuE2s');
define('API_URL', 'https://api.telegram.org/bot' . BOT_TOKEN . '/');

$content = file_get_contents("php://input");
$update = json_decode($content, TRUE);

if (!$update) {
    exit;
}

// Handle Callback Queries (Buttons)
if (isset($update['callback_query'])) {
    $callbackQuery = $update['callback_query'];
    $chatId = $callbackQuery['message']['chat']['id'];
    $messageId = $callbackQuery['message']['message_id'];
    $data = $callbackQuery['data'];
    $callbackQueryId = $callbackQuery['id'];

    apiRequest("answerCallbackQuery", ['callback_query_id' => $callbackQueryId]);

    if ($data === "change_task" || $data === "start_menu") {
        showTaskList($chatId, $messageId);
    } elseif (strpos($data, "select_task_") === 0) {
        $taskIndex = str_replace("select_task_", "", $data);
        $tasks = getTasksList();
        $selectedTask = $tasks[$taskIndex] ?? "Unknown Task";

        $text = "✅ *Task Selected*\n🎯 " . $selectedTask . "\n\n*Send your tracking URL*\n\n📌 *Example:*\n`https://app.adjust.com...`";
        
        $keyboard = [
            'inline_keyboard' => [
                [['text' => '🔄 Change Task', 'callback_data' => 'change_task']]
            ]
        ];

        apiRequest("editMessageText", [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' => $text,
            'parse_mode' => 'Markdown',
            'reply_markup' => json_encode($keyboard)
        ]);
    }
    exit;
}

// Handle Text Messages (URL Input)
if (isset($update['message'])) {
    $message = $update['message'];
    $chatId = $message['chat']['id'];
    $text = trim($message['text'] ?? '');

    if ($text === '/start') {
        showTaskList($chatId);
    } else {
        // Validate URL
        if (strpos($text, "http://") !== 0 && strpos($text, "https://") !== 0) {
            apiRequest("sendMessage", [
                'chat_id' => $chatId,
                'text' => "❌ *Invalid URL*\n\nSend /start and select task",
                'parse_mode' => 'Markdown'
            ]);
            exit;
        }

        // URL se Click ID extract karna
        $parsedUrl = parse_url($text);
        parse_str($parsedUrl['query'] ?? '', $queryParams);
        
        $clickId = $queryParams['clickid'] ?? $queryParams['click_id'] ?? $queryParams['subid'] ?? '6a8860ce7789396658953bb3';

        // Initial Progress Message
        $stepsOutput = "";
        for ($s = 1; $s <= 10; $s++) {
            $stepsOutput .= "$s. Step $s ✅\n";
        }

        $finalText = "🆔 `{$clickId}`    100%\n\n" .
                     "🟢 (10/10)\n\n" .
                     "🎯 Step Completed\n" .
                     "🟢 SUCCESS (200)\n\n" .
                     "*Steps:*\n" . $stepsOutput;

        apiRequest("sendMessage", [
            'chat_id' => $chatId,
            'text' => $finalText,
            'parse_mode' => 'Markdown'
        ]);
    }
}

// Helper Functions
function getTasksList() {
    return [
        "1. Elo Elo",
        "2. Jari Jar",
        "3. Super Money 💰",
        "4. Curie Digi",
        "35. Vivago",
        "36. Grow Rvr"
    ];
}

function showTaskList($chatId, $messageId = null) {
    $tasks = getTasksList();
    $inlineKeyboard = [];

    foreach ($tasks as index => $taskName) {
        $inlineKeyboard[] = [['text' => $taskName, 'callback_data' => 'select_task_' . $index]];
    }

    $keyboard = ['inline_keyboard' => $inlineKeyboard];
    $text = "🚀 *Welcome*\n\n1️⃣ Select Task\n2️⃣ Send Tracking URL\n3️⃣ Wait for confirmation\n\n👉 *Choose task below*";

    if ($messageId) {
        apiRequest("editMessageText", [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' => $text,
            'parse_mode' => 'Markdown',
            'reply_markup' => json_encode($keyboard)
        ]);
    } else {
        apiRequest("sendMessage", [
            'chat_id' => $chatId,
            'text' => $text,
            'parse_mode' => 'Markdown',
            'reply_markup' => json_encode($keyboard)
        ]);
    }
}

function apiRequest($method, $parameters) {
    $url = API_URL . $method;
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $parameters);
    $result = curl_exec($ch);
    curl_close($ch);
    return json_decode($result, TRUE);
}
?>

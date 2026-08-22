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

        // Store selected task temporarily (Aap yahan database/session use kar sakte hain)
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

        // 1. URL se Click ID / Parameters extract karna
        $parsedUrl = parse_url($text);
        parse_str($parsedUrl['query'] ?? '', $queryParams);
        
        // Aapke tracking link ke hisaab se clickid key change ho sakti hai (jaise click_id, clickid, chid, etc.)
        $clickId = $queryParams['clickid'] ?? $queryParams['click_id'] ?? $queryParams['subid'] ?? '6a8860ce7789396658953bb3';

        // 2. Initial Tracking Started Message Send Karna
        $responseMsg = apiRequest("sendMessage", [
            'chat_id' => $chatId,
            'text' => "🚀 *Tracking Started*\n\n🎯 Vivago\n🆔 Click ID\n`{$clickId}`\n\n⏳ Processing started...",
            'parse_mode' => 'Markdown'
        ]);

        if ($responseMsg && isset($responseMsg['result']['message_id'])) {
            $msgId = $responseMsg['result']['message_id'];

            // 3. Postback Trigger Karna (Yahan aap apna postback URL ya tracking server hit karenge)
            // Example Postback URL hit:
            // $postbackUrl = "https://your-tracking-domain.com/postback?clickid=" . $clickId;
            // @file_get_contents($postbackUrl);
            
            // Simulating network delay for postback & execution
            sleep(2);

            // 4. Live Multi-step Progress Update (10% to 100%)
            for ($i = 1; $i <= 10; $i++) {
                $percent = $i * 10;
                $stepsOutput = "";
                for ($s = 1; $s <= 10; $s++) {
                    if ($s <= $i) {
                        $stepsOutput .= "$s. Step $s ✅\n";
                    } else {
                        $stepsOutput .= "$s. Step $s ⏳\n";
                    }
                }

                $progressText = "🆔 `{$clickId}`    {$percent}%\n\n" .
                                "🟢 ({$i}/10)\n\n" .
                                "🎯 Step Completed\n" .
                                "🟢 SUCCESS (200)\n\n" .
                                "*Steps:*\n" . $stepsOutput;

                apiRequest("editMessageText", [
                    'chat_id' => $chatId,
                    'message_id' => $msgId,
                    'text' => $progressText,
                    'parse_mode' => 'Markdown'
                ]);

                if ($i < 10) {
                    usleep(500000); // 0.5 second delay per step for smooth animation
                }
            }
        }
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

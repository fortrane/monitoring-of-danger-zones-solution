<?php

require_once __DIR__ . "/requirements/Medoo/connect.php";
require_once __DIR__ . '/app/controllers/LogsController.php';

use App\Controllers\LogsController;

$logsController = new LogsController($database);

if (isset($_GET['action'])) {
    $action = $_GET['action'];

    switch ($action) {
        case 'getAllLogs':
            $logsController->getAllLogs();
            break;

        case 'getCountLogs':
            $logsController->getCountLogs();
            break;

        case 'deleteAllLogs':
            $logsController->deleteAllLogs();
            break;

        case 'addLog':
            if ($_SERVER['REQUEST_METHOD'] == 'POST') {
                $jsonData = json_decode(file_get_contents('php://input'), true);
                $logsController->addLog($jsonData);
            } else {
                header("HTTP/1.1 405 Method Not Allowed");
            }
            break;

        default:
            header("HTTP/1.1 404 Not Found");
            break;
    }
} else {
    header("HTTP/1.1 404 Not Found");
}

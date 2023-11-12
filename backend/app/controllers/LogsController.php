<?php

namespace App\Controllers;

date_default_timezone_set("Europe/Moscow");

include_once __DIR__ . '/../../requirements/Medoo/connect.php';

class LogsController {

    public $database;

    public function __construct($database) {
        $this->database = $database;

    }

    public function getAllLogs() {
        $logs = $this->database->select("cv_all_logs", [
            "id",
            "camera",
            "walk_in_rate",
            "image",
            "detection",
            "created_at"
        ],
        [
            "ORDER" => [
                "id" => "DESC",
            ]      
        ]);
        
        header('Content-Type: application/json');
        echo json_encode($logs);
    }

    public function addLog($logData) {

        $this->database->insert("cv_all_logs", [
            "camera" => $logData["camera"],
            "walk_in_rate" => $logData["walk_in_rate"],
            "image" => $logData["image"],
            "detection" => $logData["detection"],
            "created_at" => date('Y-m-d H:i:s')
        ]);

        if ($this->database->id()) {
            echo json_encode(['status' => 'success', 'log_id' => $this->database->id()]);
        } else {
            echo json_encode(['status' => 'error1']);
        }

    }

    public function getCountLogs() {
        $logs = $this->database->count("cv_all_logs");
        
        header('Content-Type: application/json');
        echo json_encode(['count' => $logs]);
    }

    public function deleteAllLogs() {
        $logs = $this->database->delete("cv_all_logs", []);
        
        header('Content-Type: application/json');
        echo json_encode(['status' => 'success']);
    }
}

import cv2
from ultralytics import YOLO
import numpy as np
import time
import datetime
import requests
import matplotlib.pyplot as plt
import os
import base64
import io


def draw_people(image, vertices, transparency=0.5):

    mask = np.zeros_like(image)
    vertices_array = np.array([vertices], np.int32)
    cv2.fillPoly(image, vertices_array, color=(0, 0, 255))
    area = cv2.contourArea(vertices_array)

    return


def detect_square(image, color):
    upper_color = np.array(color)
    maska = cv2.inRange(image, upper_color, upper_color)

    area_danger = cv2.countNonZero(maska)
    return area_danger


def draw_polygon(image, vertices, transparency=0.5):

    vertices_array = np.array([vertices], np.int32)
    cv2.fillPoly(image, vertices_array, color=(123, 200, 0, 255))
    area = cv2.contourArea(vertices_array)

    return


def coordinates(cam_name):

    zone_count = count_txt_files_with_zones(cam_name)

    if zone_count == 1:
        file_path = "dataset/danger_zones/danger_" + cam_name + ".txt"

        with open(file_path, "r") as file:
            file_data = file.read().split(",\n")

        matrix = [
            [
                list(map(int, pair.strip("[] \n").split(",")))
                for pair in file_data
                if pair.strip()
            ]
        ]

        return matrix
    else:
        all_zones = []

        for zone_num in range(1, zone_count + 1):
            zone_file_path = (
                f"dataset/danger_zones/danger_{cam_name}_zone{zone_num}.txt"
            )

            with open(zone_file_path, "r") as file:
                file_data = file.read().split(",\n")

            zone_coordinates = [
                list(map(int, pair.strip("[] \n").split(",")))
                for pair in file_data
                if pair.strip()
            ]
            all_zones.append(zone_coordinates)

        return all_zones


def count_txt_files_with_zones(cam_name):
    folder_path = "dataset/danger_zones"
    file_prefix = f"danger_{cam_name}"

    similar_files = [
        file
        for file in os.listdir(folder_path)
        if file.startswith(file_prefix) and file.lower().endswith(".txt")
    ]

    return len(similar_files)


def predict(
    image_path, danger_zones, path_crop, cam_name, shape_crop=2, save_crop=False
):
    try:
        detect = False

        results = []

        start_time = time.time()
        image = cv2.imread(image_path)

        resized_width = image.shape[1] // shape_crop
        resized_height = image.shape[0] // shape_crop
        image = cv2.resize(image, (resized_width, resized_height))

        model2 = YOLO("segment.pt")
        results2 = model2(
            source=image,
            show=True,
            conf=0.5,
            classes=[0],
            boxes=False,
            save_crop=save_crop,
        )
        mask = results2[0].masks
        image_original = image.copy()
        for danger_zone in danger_zones:
            detecting_and_drawing2(image, mask, shape_crop, danger_zone)
    except Exception as e:
        print("Error:", type(e).__name__)

    end_time = time.time()
    work_time = end_time - start_time
    print(f"Work_time: {work_time/3}")
    show(image)
    return results


def detecting_and_drawing(image, mask, shape_crop, danger_zone):
    detect = False

    results = []
    area_peoples = []
    print("NEW DANGER")

    print(danger_zone)
    danger_area_vertices = [(x / shape_crop, y / shape_crop) for x, y in danger_zone]
    draw_polygon(image, danger_area_vertices)

    if mask != None:

        area_danger = detect_square(image, [123, 200, 0])

        percents = []

        for a in range(len(mask.xy)):
            points = mask.xy[a].astype(int)

            draw_people(image, points)

            area_people = detect_square(image, [0, 0, 255]) - sum(area_peoples)
            print(f"NEW WORKER: {a} {points[0]} {area_people}")
            area_without_person_count = detect_square(image, [123, 200, 0]) + sum(
                area_peoples
            )
            print(f"SUM AREA {sum(area_peoples)}")
            area_peoples.append(area_people)

            percent = (
                (int(area_danger) - int(area_without_person_count)) / int(area_people)
            ) * 100
            print("Площадь чела в пикселях:", area_people)
            print(percent)

            image_crop = last_crop(path_crop)

            print(percent)
            if percent > 0:

                if percent > 15:
                    detect = 1

                    result = {
                        "camera": cam_name,
                        "walk_in_rate": percent,
                        "image": image_crop,
                        "detection": detect,
                    }
                    response(result)
                    results.append(result)
                else:
                    detect = 0
                    result = {
                        "camera": cam_name,
                        "walk_in_rate": percent,
                        "image": image_crop,
                        "detection": detect,
                    }
                    response(result)
                    results.append(result)
        detect = False
        area_peoples = []

    else:
        print("Нет людей")

    return results


def detecting_and_drawing2(image, mask, shape_crop, danger_zone):
    detect = False

    results = []

    danger_area_vertices = [(x / shape_crop, y / shape_crop) for x, y in danger_zone]
    draw_polygon(image, danger_area_vertices)

    if mask != None:

        area_danger = detect_square(image, [123, 200, 0])
        print("Площадь полигона в пикселях:", area_danger)

        area_peoples = []
        percents = []
        try:
            for a in range(len(mask.xy)):
                points = mask.xy[a].astype(int)
                draw_people(image, points)
                area_people = detect_square(image, [0, 0, 255]) - sum(area_peoples)
                area_without_person_count = detect_square(image, [123, 200, 0]) + sum(
                    area_peoples
                )

                area_peoples.append(area_people)

                percent = (
                    (int(area_danger) - int(area_without_person_count))
                    / int(area_people)
                ) * 100
                print("Площадь чела в пикселях:", area_people)
                print("Площадь полигона без чела", int(area_without_person_count))
                print(percent)

                image_crop = last_crop(path_crop)

                if percent > 0:
                    if percent > 15:
                        detect = True

                        result = {
                            "camera": cam_name,
                            "walk_in_rate": percent,
                            "image": image_crop,
                            "detection": detect,
                        }
                        response(result)
                        print(response)

                        results.append(result)
                    else:
                        detect = False
                        result = {
                            "camera": cam_name,
                            "walk_in_rate": percent,
                            "image": image_crop,
                            "detection": detect,
                        }
                        response(result)
                        results.append(result)

            area_peoples = []
            detect = False

        except Exception as e:
            print("Error:", type(e).__name__)
    else:
        print("Нет людей")


def response(result):
    print(result)
    url = "http://120.0.0.0/kngksangjkhndsjkgg/backend/?action=addLog"
    response = requests.post(url, json=result)
    print(response)


def last_crop(path_crop):
    jpg_files = [f for f in os.listdir(path_crop) if f.lower().endswith(".jpg")]
    if jpg_files:
        latest_jpg_file = (
            path_crop
            + "\\"
            + max(jpg_files, key=lambda x: os.path.getmtime(os.path.join(path_crop, x)))
        )

        image_crop = cv2.imread(latest_jpg_file)
        image_crop = "data:image/jpeg;base64," + cv2_to_base64(image_crop)
    return image_crop


def cv2_to_base64(image):
    is_success, buffer = cv2.imencode(".jpg", image)
    if is_success:
        base64_str = base64.b64encode(buffer).decode("utf-8")
        return base64_str
    else:
        return None


def show(image):

    cv2.imshow("Image with Results", image)
    filename = "_result.jpg"
    cv2.imwrite(filename, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def start(cam_name, image_path):
    path = "runs\\segment"
    all_folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    predict_folders = [f for f in all_folders if f.startswith("predict")]
    latest_predict_folder = max(
        predict_folders, key=lambda x: os.path.getmtime(os.path.join(path, x))
    )
    path_crop = (
        "runs\\segment"
        + "\\"
        + latest_predict_folder[:-1]
        + str(int(latest_predict_folder[-1]) + 1)
        + "\\crops\\person"
    )

    danger_zone = coordinates(cam_name)
    predict(
        image_path,
        danger_zone,
        path_crop,
        cam_name=cam_name,
        shape_crop=2,
        save_crop=True,
    )

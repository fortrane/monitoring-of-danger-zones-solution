const apiRequestDataLink = "https://127.0.0.1/backend/";

const grid = new gridjs.Grid({
    search: true,
    pagination: true,
    columns: [{
            id: "id",
            name: "ID",
            sort: true,
        },
        {
            id: "camera",
            name: "Camera",
        },
        {
            id: "detection",
            name: "Detection",
            formatter: (cell) => {
                let detection = "";
                if(parseInt(cell) == 1) {
                    detection = `<span class="inline-flex items-center gap-x-1.5 rounded-full px-2 py-1 text-xs font-medium text-gray-900 ring-1 ring-inset ring-gray-200"> <svg class="h-1.5 w-1.5 fill-green-500" viewBox="0 0 6 6" aria-hidden="true"> <circle cx="3" cy="3" r="3" /> </svg> Detected </span>`;
                } else {
                    detection = `<span class="inline-flex items-center gap-x-1.5 rounded-full px-2 py-1 text-xs font-medium text-gray-900 ring-1 ring-inset ring-gray-200"> <svg class="h-1.5 w-1.5 fill-red-500" viewBox="0 0 6 6" aria-hidden="true"> <circle cx="3" cy="3" r="3" /> </svg> Undeteced </span>`;
                }

                return gridjs.html(detection)
            }
        },
        {
            id: "walk_in_rate",
            name: "Walk In Rate (%)",
            formatter: (cell) => {
                let badge = "";
                if(parseInt(cell) <= 30) {
                    badge = `<span class="inline-flex items-center gap-x-1.5 rounded-md bg-green-100 px-1.5 py-0.5 text-xs font-medium text-green-700"> <svg class="h-1.5 w-1.5 fill-green-500" viewBox="0 0 6 6" aria-hidden="true"> <circle cx="3" cy="3" r="3" /> </svg> ${cell}% </span>`;
                } else {
                    badge = `<span class="inline-flex items-center gap-x-1.5 rounded-md bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-700"> <svg class="h-1.5 w-1.5 fill-red-500" viewBox="0 0 6 6" aria-hidden="true"> <circle cx="3" cy="3" r="3" /> </svg> ${cell}% </span>`;
                }

                return gridjs.html(badge)
            }
        },
        {
            id: "image",
            name: "Image",
            formatter: (cell) => {
                let image = "";

                image = `<div class="cursor-pointer">
                            <img src="${cell}" class="rounded-[4px] h-8 w-8 preview" >
                        </div>`

                return gridjs.html(image)
            }
        },
        {
            id: "created_at",
            name: "Created At",
            formatter: (cell) => {
                return gridjs.html(`<span class="inline-flex items-center rounded-md bg-sky-100 px-1.5 py-0.5 text-xs font-medium text-sky-700">${cell}</span>`)
            }
        }
    ],
    server: {
        url: apiRequestDataLink + "?action=getAllLogs",
        then: data => data
    },
    className: {
        td: '!py-1 !max-w-[160px]',
        th: '!max-w-[160px]'
    }
});

function initialRenderTable() {
    getCountOfLogs().then((result) => {
        previousCount = result.count;
        grid.render(document.getElementById("wrapper"));
    });
}

function rerenderTable() {
    grid.updateConfig({
        server: {
            url: apiRequestDataLink + "?action=getAllLogs",
            then: data => data
        }
    }).forceRender();

    reInitListeners();
}

$(document).ready(() => {
    initialRenderTable();
    initUpdatesInterval();
    initMutationObserver();

    initListeners();
});

let previousCount = 0;

function initUpdatesInterval() {
    setInterval(() => {
        getCountOfLogs().then((result) => {
            if (result.count > previousCount) {
                previousCount = result.count;
                rerenderTable();
                pushNewLogAlert();
            } else if (result.count < previousCount) {
                previousCount = result.count;
                rerenderTable();
            }
        });
    }, 3000);
}


function pushNewLogAlert() {
    toastr.warning('Someone is in danger! Check the employee!', 'Attention, new entry!')
}

function getCountOfLogs() {
    return new Promise((resolve, reject) => {
        $.ajax({
            type: "GET",
            url: apiRequestDataLink + "?action=getCountLogs",
            success: function(data) {
                resolve(data);
            },
            error: function(error) {
                reject(error);
            }
        });
    });
}

function deleteAllLogs() {
    return new Promise((resolve, reject) => {
        $.ajax({
            type: "GET",
            url: apiRequestDataLink + "?action=deleteAllLogs",
            success: function(data) {
                resolve(data);
            },
            error: function(error) {
                reject(error);
            }
        });
    });
}

function reInitListeners() {

    $(".delete-button").off("click");

    $(".delete-button").click((event) => {
    
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {

                deleteAllLogs().then(data => {
                    toastr.success('You have successfully deleted the logs', 'Changes have been saved!');
                });
            }
        });
    });    
    
}

function initListeners() {

    $(".delete-button").click((event) => {
    
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {

                deleteAllLogs().then(data => {
                    toastr.success('You have successfully deleted the logs', 'Changes have been saved!');
                });
            }
        });
    });    
    
}

function initMutationObserver() {
    const wrapper = document.getElementById("wrapper");

    const observer = new MutationObserver((mutationsList) => {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                reInitListeners();
            }
        }
    });

    observer.observe(wrapper, { childList: true, subtree: true });
}

function handlePreviewClick() {
    const previewScreen = document.querySelector('.preview-screen');
    const previewImage = document.querySelector('.preview-image');

    previewImage.src = this.src;
    previewScreen.classList.remove('hidden');
}

function handleScreenClick() {
    this.classList.add('hidden');
}

function reInitListeners() {
    const previews = document.querySelectorAll('.preview');
    const previewScreen = document.querySelector('.preview-screen');

    previews.forEach(preview => {
        preview.removeEventListener('click', handlePreviewClick);
    });
    previewScreen.removeEventListener('click', handleScreenClick);

    previews.forEach(preview => {
        preview.addEventListener('click', handlePreviewClick);
    });
    previewScreen.addEventListener('click', handleScreenClick);
}
let medicines = [];

let editingMedicineId = null;


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            await loadCurrentUser();

            await loadMedicines();

            setupMedicineForm();

            setupMedicineSearch();

            setupMedicineRefresh();

            setupCancelEdit();

        }
        catch (error) {

            console.error(
                "Admin Medicine Error:",
                error
            );

            showMedicineAlert(
                error.message ||
                "Không thể tải dữ liệu thuốc.",
                "danger"
            );

        }

    }
);

async function loadMedicines() {

    const response =
        await apiFetch(
            "/api/medicine"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải danh sách thuốc."
        );

    }


    medicines =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderMedicines(
        medicines
    );

}

function renderMedicines(
    items
) {

    const tbody =
        document.getElementById(
            "medicineList"
        );


    if (!tbody) {

        return;

    }


    if (!items.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="6"
                    class="text-center
                           py-5
                           text-secondary">

                    Không tìm thấy thuốc.

                </td>

            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        items
            .map(
                medicine => {

                    const statusBadge =
                        medicine.status ===
                        "Active"

                            ? `
                                <span
                                    class="badge
                                           text-bg-success">

                                    Đang sử dụng

                                </span>
                            `

                            : `
                                <span
                                    class="badge
                                           text-bg-secondary">

                                    Ngừng sử dụng

                                </span>
                            `;


                    const stockClass =
                        Number(
                            medicine.stock_qty
                        ) <= 0

                            ? "text-danger fw-semibold"

                            : Number(
                                medicine.stock_qty
                              ) <= 10

                                ? "text-warning fw-semibold"

                                : "text-success";


                    return `
                        <tr>

                            <td>

                                <div
                                    class="fw-semibold">

                                    ${escapeHtml(
                                        medicine.name ||
                                        ""
                                    )}

                                </div>

                            </td>


                            <td>

                                ${escapeHtml(
                                    medicine.unit ||
                                    ""
                                )}

                            </td>


                            <td>

                                ${formatCurrency(
                                    medicine.price
                                )}

                            </td>


                            <td>

                                <span
                                    class="${stockClass}">

                                    ${
                                        medicine.stock_qty ??
                                        0
                                    }

                                </span>

                            </td>


                            <td>

                                ${statusBadge}

                            </td>


                            <td
                                class="text-end">

                                <div
                                    class="d-flex
                                           justify-content-end
                                           gap-2">

                                    <button
                                        type="button"
                                        class="btn
                                               btn-sm
                                               btn-outline-primary"
                                        data-edit-medicine="${medicine.medicine_id}">

                                        <i
                                            class="bi bi-pencil">
                                        </i>

                                    </button>


                                    ${
                                        medicine.status ===
                                        "Active"

                                            ? `
                                                <button
                                                    type="button"
                                                    class="btn
                                                           btn-sm
                                                           btn-outline-danger"
                                                    data-discontinue-medicine="${medicine.medicine_id}">

                                                    <i
                                                        class="bi bi-pause-circle">
                                                    </i>

                                                </button>
                                              `
                                            : ""
                                    }

                                </div>

                            </td>

                        </tr>
                    `;

                }
            )
            .join("");


    bindMedicineActions();

}

function bindMedicineActions() {

    document
        .querySelectorAll(
            "[data-edit-medicine]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        editMedicine(
                            Number(
                                button.dataset.editMedicine
                            )
                        );

                    }
                );

            }
        );


    document
        .querySelectorAll(
            "[data-discontinue-medicine]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        discontinueMedicine(
                            Number(
                                button.dataset
                                    .discontinueMedicine
                            )
                        );

                    }
                );

            }
        );

}
function setupMedicineForm() {

    const form =
        document.getElementById(
            "medicineForm"
        );


    if (!form) {

        return;

    }


    form.addEventListener(
        "submit",
        saveMedicine
    );

}

async function saveMedicine(
    event
) {

    event.preventDefault();


    const name =
        document
            .getElementById(
                "medicineName"
            )
            .value
            .trim();


    const unit =
        document
            .getElementById(
                "medicineUnit"
            )
            .value
            .trim();


    const price =
        Number(
            document
                .getElementById(
                    "medicinePrice"
                )
                .value
        );


    const stock =
        Number(
            document
                .getElementById(
                    "medicineStock"
                )
                .value
        );


    const status =
        document
            .getElementById(
                "medicineStatus"
            )
            .value;


    if (!name) {

        showMedicineAlert(
            "Vui lòng nhập tên thuốc.",
            "danger"
        );

        return;

    }


    if (!unit) {

        showMedicineAlert(
            "Vui lòng nhập đơn vị.",
            "danger"
        );

        return;

    }


    if (
        !Number.isFinite(price) ||
        price < 0
    ) {

        showMedicineAlert(
            "Đơn giá không hợp lệ.",
            "danger"
        );

        return;

    }


    if (
        !Number.isInteger(stock) ||
        stock < 0
    ) {

        showMedicineAlert(
            "Tồn kho phải là số nguyên không âm.",
            "danger"
        );

        return;

    }


    const payload = {

        name:
            name,

        unit:
            unit,

        price:
            price,

        stock_qty:
            stock,

        status:
            status,

    };


    const isEditing =
        editingMedicineId !== null;


    const url =
        isEditing

            ? `/api/medicine/${editingMedicineId}`

            : "/api/medicine";


    const method =
        isEditing
            ? "PATCH"
            : "POST";


    const response =
        await apiFetch(
            url,
            {

                method:
                    method,

                body:
                    JSON.stringify(
                        payload
                    ),

            }
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            (
                isEditing
                    ? "Không thể cập nhật thuốc."
                    : "Không thể tạo thuốc."
            )
        );

    }


    showMedicineAlert(
        isEditing
            ? "Đã cập nhật thuốc."
            : "Đã thêm thuốc.",
        "success"
    );


    resetMedicineForm();


    await loadMedicines();

}

function editMedicine(
    medicineId
) {

    const medicine =
        medicines.find(
            item =>
                Number(
                    item.medicine_id
                ) ===
                Number(
                    medicineId
                )
        );


    if (!medicine) {

        showMedicineAlert(
            "Không tìm thấy thuốc.",
            "danger"
        );

        return;

    }


    editingMedicineId =
        medicine.medicine_id;


    document.getElementById(
        "medicineId"
    ).value =
        medicine.medicine_id;


    document.getElementById(
        "medicineName"
    ).value =
        medicine.name || "";


    document.getElementById(
        "medicineUnit"
    ).value =
        medicine.unit || "";


    document.getElementById(
        "medicinePrice"
    ).value =
        medicine.price ?? 0;


    document.getElementById(
        "medicineStock"
    ).value =
        medicine.stock_qty ?? 0;


    document.getElementById(
        "medicineStatus"
    ).value =
        medicine.status || "Active";


    document.getElementById(
        "medicineFormTitle"
    ).textContent =
        "Sửa thuốc";


    const submitButton =
        document.getElementById(
            "medicineSubmitButton"
        );


    submitButton.innerHTML = `
        <i
            class="bi bi-check-lg me-1">
        </i>

        Lưu thay đổi
    `;


    document
        .getElementById(
            "cancelMedicineEdit"
        )
        .classList
        .remove("d-none");


    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });

}

function setupCancelEdit() {

    document
        .getElementById(
            "cancelMedicineEdit"
        )
        ?.addEventListener(
            "click",
            resetMedicineForm
        );

}

function resetMedicineForm() {

    editingMedicineId =
        null;


    document
        .getElementById(
            "medicineForm"
        )
        .reset();


    document.getElementById(
        "medicineId"
    ).value = "";


    document.getElementById(
        "medicineStatus"
    ).value =
        "Active";


    document.getElementById(
        "medicineFormTitle"
    ).textContent =
        "Thêm thuốc";


    document.getElementById(
        "medicineSubmitButton"
    ).innerHTML = `
        <i
            class="bi bi-plus-lg me-1">
        </i>

        Thêm thuốc
    `;


    document
        .getElementById(
            "cancelMedicineEdit"
        )
        .classList
        .add("d-none");

}

async function discontinueMedicine(
    medicineId
) {

    const medicine =
        medicines.find(
            item =>
                Number(
                    item.medicine_id
                ) ===
                Number(
                    medicineId
                )
        );


    if (!medicine) {

        return;

    }


    const confirmed =
        window.confirm(
            `Bạn có chắc muốn ngừng sử dụng thuốc "${medicine.name}"?`
        );


    if (!confirmed) {

        return;

    }


    const response =
        await apiFetch(
            `/api/medicine/${medicineId}`,
            {

                method: "PATCH",

                body:
                    JSON.stringify({

                        status:
                            "Discontinued",

                    }),

            }
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể ngừng sử dụng thuốc."
        );

    }


    showMedicineAlert(
        "Đã chuyển thuốc sang trạng thái ngừng sử dụng.",
        "success"
    );


    await loadMedicines();

}

function setupMedicineSearch() {

    const searchInput =
        document.getElementById(
            "medicineSearch"
        );


    if (!searchInput) {

        return;

    }


    searchInput.addEventListener(
        "input",
        () => {

            const keyword =
                searchInput.value
                    .trim()
                    .toLowerCase();


            const filtered =
                medicines.filter(
                    medicine => {

                        const name =
                            String(
                                medicine.name ||
                                ""
                            )
                            .toLowerCase();


                        return name.includes(
                            keyword
                        );

                    }
                );


            renderMedicines(
                filtered
            );

        }
    );

}

function setupMedicineRefresh() {

    document
        .getElementById(
            "refreshMedicines"
        )
        ?.addEventListener(
            "click",
            async () => {

                try {

                    await loadMedicines();

                }
                catch (error) {

                    showMedicineAlert(
                        error.message ||
                        "Không thể tải lại thuốc.",
                        "danger"
                    );

                }

            }
        );

}

function showMedicineAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "medicineAlert"
        );


    if (!alert) {

        return;

    }


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );


    setTimeout(
        () => {

            alert.classList.add(
                "d-none"
            );

        },
        4000
    );

}
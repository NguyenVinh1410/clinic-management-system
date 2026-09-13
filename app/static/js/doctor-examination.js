let appointment = null;

let medicalRecord = null;

let medicines = [];

let prescription = null;


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            await loadAppointment();

            await loadMedicines();

            await loadMedicalHistory();

            await loadExistingRecord();

            setupEvents();

        }
        catch (error) {

            console.error(error);

            showExaminationAlert(
                error.message ||
                "Không thể tải dữ liệu khám.",
                "danger"
            );

        }

    }
);


async function loadAppointment() {

    const response =
        await apiFetch(
            `/api/appointment/${window.DOCTOR_APPOINTMENT_ID}`
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải lịch khám."
        );

    }


    appointment = data;


    document.getElementById(
        "patientName"
    ).textContent =
        appointment.patient_name;


    document.getElementById(
        "patientId"
    ).textContent =
        `#${appointment.patient_id}`;


    document.getElementById(
        "patientPhone"
    ).textContent =
        appointment.patient_phone ||
        "Chưa cập nhật";


    document.getElementById(
        "appointmentTime"
    ).textContent =
        formatDateTime(
            appointment.appointment_time
        );


    document.getElementById(
        "appointmentStatus"
    ).innerHTML =
        renderStatusBadge(
            appointment.status
        );


    if (
        appointment.status !==
        "Confirmed"
    ) {

        document.getElementById(
            "medicalRecordForm"
        )
        .querySelectorAll(
            "input, textarea, button"
        )
        .forEach(
            element => {

                element.disabled = true;

            }
        );

    }

}


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
            ? data.filter(
                medicine =>
                    medicine.status ===
                    "Active"
            )
            : [];

}


async function loadExistingRecord() {

    try {

        const response =
            await apiFetch(
                `/api/medical_record/appointment/${window.DOCTOR_APPOINTMENT_ID}`
            );


        const data =
            await parseApiResponse(
                response
            );


        if (
            response.ok
        ) {

            medicalRecord =
                data;


            fillMedicalRecord(
                medicalRecord
            );


            await loadPrescription(
                medicalRecord.record_id
            );

        }

    }
    catch (error) {

        console.error(error);

    }

}


function fillMedicalRecord(
    record
) {

    document.getElementById(
        "symptoms"
    ).value =
        record.symptoms ||
        "";


    document.getElementById(
        "diagnosis"
    ).value =
        record.diagnosis ||
        "";


    document.getElementById(
        "medicalNote"
    ).value =
        record.note ||
        "";


    if (record.examined_at) {

        const date =
            new Date(
                record.examined_at
            );


        const local =
            new Date(
                date.getTime() -
                date.getTimezoneOffset() *
                60000
            )
            .toISOString()
            .slice(
                0,
                16
            );


        document.getElementById(
            "examinedAt"
        ).value =
            local;

    }

}


async function loadPrescription(
    recordId
) {

    const response =
        await apiFetch(
            `/api/prescription/record/${recordId}`
        );


    if (!response.ok) {

        return;

    }


    const data =
        await parseApiResponse(
            response
        );


    prescription = data;


    renderPrescription(
        prescription
    );

}


function renderPrescription(
    data
) {

    const container =
        document.getElementById(
            "prescriptionRows"
        );


    container.innerHTML = "";


    if (
        !data ||
        !data.details ||
        !data.details.length
    ) {

        addMedicineRow();

        return;

    }


    data.details.forEach(
        detail => {

            addMedicineRow(
                detail
            );

        }
    );

}


function createMedicineOptions(
    selectedId = null
) {

    return medicines
        .map(
            medicine => `
                <option
                    value="${medicine.medicine_id}"
                    ${Number(
                        medicine.medicine_id
                    ) === Number(
                        selectedId
                    )
                        ? "selected"
                        : ""
                    }>

                    ${escapeHtml(
                        medicine.name
                    )}
                    -
                    ${formatCurrency(
                        medicine.price
                    )}

                </option>
            `
        )
        .join("");

}


function addMedicineRow(
    detail = null
) {

    const container =
        document.getElementById(
            "prescriptionRows"
        );


    const row =
        document.createElement(
            "div"
        );


    row.className =
        "border rounded p-3 mb-3 medicine-row";


    row.innerHTML = `

        <div class="row g-3">

            <div class="col-12 col-md-6">

                <label class="form-label small fw-semibold">
                    Thuốc
                </label>

                <select class="form-select medicine-id">

                    <option value="">
                        Chọn thuốc
                    </option>

                    ${createMedicineOptions(
                        detail?.medicine_id
                    )}

                </select>

            </div>


            <div class="col-6 col-md-3">

                <label class="form-label small fw-semibold">
                    Số lượng
                </label>

                <input
                    type="number"
                    min="1"
                    class="form-control medicine-quantity"
                    value="${
                        detail?.quantity ||
                        1
                    }">

            </div>


            <div class="col-6 col-md-3">

                <label class="form-label small fw-semibold">
                    Thao tác
                </label>

                <button
                    type="button"
                    class="btn btn-outline-danger w-100 remove-medicine">

                    <i class="bi bi-trash"></i>

                </button>

            </div>


            <div class="col-12">

                <label class="form-label small fw-semibold">
                    Liều dùng
                </label>

                <input
                    type="text"
                    class="form-control medicine-dosage"
                    maxlength="255"
                    value="${
                        detail?.dosage ||
                        ""
                    }"
                    placeholder="Ví dụ: 2 viên/ngày">

            </div>


            <div class="col-12">

                <label class="form-label small fw-semibold">
                    Cách dùng
                </label>

                <input
                    type="text"
                    class="form-control medicine-usage"
                    maxlength="500"
                    value="${
                        detail?.usage_note ||
                        ""
                    }"
                    placeholder="Ví dụ: Uống sau ăn">

            </div>

        </div>
    `;


    row
        .querySelector(
            ".remove-medicine"
        )
        .addEventListener(
            "click",
            () => row.remove()
        );


    container.appendChild(
        row
    );

}


async function saveMedicalRecord(
    event
) {

    event.preventDefault();


    if (
        !appointment ||
        appointment.status !==
        "Confirmed"
    ) {

        showExaminationAlert(
            "Lịch khám chưa ở trạng thái có thể khám.",
            "danger"
        );

        return;

    }


    const diagnosis =
        document.getElementById(
            "diagnosis"
        ).value.trim();


    if (!diagnosis) {

        showExaminationAlert(
            "Chẩn đoán không được để trống.",
            "danger"
        );

        return;

    }


    const payload = {

        symptoms:
            document
                .getElementById(
                    "symptoms"
                )
                .value
                .trim() ||
            null,

        diagnosis,

        note:
            document
                .getElementById(
                    "medicalNote"
                )
                .value
                .trim() ||
            null,

        examined_at:
            new Date(
                document.getElementById(
                    "examinedAt"
                ).value
            ).toISOString(),

    };


    try {

        let response;


        if (medicalRecord) {

            response =
                await apiFetch(
                    `/api/medical_record/${medicalRecord.record_id}`,
                    {
                        method: "PATCH",
                        body: JSON.stringify(
                            payload
                        ),
                    }
                );

        }
        else {

            payload.appointment_id =
                appointment.appointment_id;


            response =
                await apiFetch(
                    "/api/medical_record",
                    {
                        method: "POST",
                        body: JSON.stringify(
                            payload
                        ),
                    }
                );

        }


        const data =
            await parseApiResponse(
                response
            );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Không thể lưu hồ sơ."
            );

        }


        medicalRecord =
            data;


        showExaminationAlert(
            "Đã lưu hồ sơ khám.",
            "success"
        );

    }
    catch (error) {

        console.error(error);

        showExaminationAlert(
            error.message ||
            "Lưu hồ sơ thất bại.",
            "danger"
        );

    }

}


async function savePrescription() {

    if (!medicalRecord) {

        showExaminationAlert(
            "Hãy lưu hồ sơ khám trước khi kê đơn.",
            "warning"
        );

        return;

    }


    const rows =
        [
            ...document.querySelectorAll(
                ".medicine-row"
            )
        ];


    const details =
        [];


    for (
        const row of rows
    ) {

        const medicineId =
            Number(
                row.querySelector(
                    ".medicine-id"
                ).value
            );


        const quantity =
            Number(
                row.querySelector(
                    ".medicine-quantity"
                ).value
            );


        const dosage =
            row.querySelector(
                ".medicine-dosage"
            ).value.trim();


        const usageNote =
            row.querySelector(
                ".medicine-usage"
            ).value.trim();


        if (
            !medicineId ||
            quantity <= 0 ||
            !dosage
        ) {

            showExaminationAlert(
                "Thông tin thuốc chưa đầy đủ.",
                "danger"
            );

            return;

        }


        details.push({

            medicine_id:
                medicineId,

            quantity,

            dosage,

            usage_note:
                usageNote ||
                null,

        });

    }


    if (!details.length) {

        showExaminationAlert(
            "Đơn thuốc phải có ít nhất một thuốc.",
            "danger"
        );

        return;

    }


    const uniqueIds =
        new Set(
            details.map(
                item =>
                    item.medicine_id
            )
        );


    if (
        uniqueIds.size !==
        details.length
    ) {

        showExaminationAlert(
            "Không được kê cùng một thuốc nhiều lần.",
            "danger"
        );

        return;

    }


    try {

        let response;


        if (prescription) {

            response =
                await apiFetch(
                    `/api/prescription/${prescription.prescription_id}`,
                    {
                        method: "PATCH",
                        body: JSON.stringify({
                            details
                        }),
                    }
                );

        }
        else {

            response =
                await apiFetch(
                    "/api/prescription",
                    {
                        method: "POST",
                        body: JSON.stringify({

                            record_id:
                                medicalRecord.record_id,

                            details,

                        }),
                    }
                );

        }


        const data =
            await parseApiResponse(
                response
            );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Không thể lưu đơn thuốc."
            );

        }


        prescription =
            data;


        showExaminationAlert(
            "Đã lưu đơn thuốc.",
            "success"
        );

    }
    catch (error) {

        console.error(error);

        showExaminationAlert(
            error.message ||
            "Lưu đơn thuốc thất bại.",
            "danger"
        );

    }

}


async function completeAppointment() {

    if (!medicalRecord) {

        showExaminationAlert(
            "Hãy lưu hồ sơ khám trước.",
            "warning"
        );

        return;

    }


    const confirmed =
        confirm(
            "Xác nhận hoàn tất lượt khám?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await apiFetch(
                `/api/appointment/${appointment.appointment_id}/status`,
                {
                    method: "PATCH",

                    body: JSON.stringify({
                        status: "Completed",
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
                "Không thể hoàn tất lượt khám."
            );

        }


        appointment =
            data;


        document.getElementById(
            "appointmentStatus"
        ).innerHTML =
            renderStatusBadge(
                appointment.status
            );


        document.getElementById(
            "completeAppointmentButton"
        ).disabled = true;


        showExaminationAlert(
            "Lượt khám đã hoàn tất.",
            "success"
        );

    }
    catch (error) {

        console.error(error);

        showExaminationAlert(
            error.message ||
            "Không thể hoàn tất lượt khám.",
            "danger"
        );

    }

}


async function loadMedicalHistory() {

    const response =
        await apiFetch(
            `/api/medical_history/appointment/${window.DOCTOR_APPOINTMENT_ID}/previous`
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        document.getElementById(
            "medicalHistory"
        ).innerHTML = `
            <div class="text-secondary small">
                Chưa có lịch sử khám trước đó.
            </div>
        `;

        return;

    }


    renderMedicalHistory(
        data.items || []
    );

}


function renderMedicalHistory(
    items
) {

    const container =
        document.getElementById(
            "medicalHistory"
        );


    if (!items.length) {

        container.innerHTML = `
            <div class="text-secondary small">

                Chưa có lần khám trước đó.

            </div>
        `;

        return;

    }


    container.innerHTML =
        items.map(
            item => `

                <div class="border rounded p-3 mb-3">

                    <div class="small text-secondary mb-1">

                        ${formatDateTime(
                            item.appointment_time
                        )}

                    </div>


                    <div class="fw-semibold mb-1">

                        ${escapeHtml(
                            item.doctor_name
                        )}

                    </div>


                    <div class="small mb-2">

                        ${escapeHtml(
                            item.specialty_name ||
                            ""
                        )}

                    </div>


                    <div class="small">

                        <strong>
                            Chẩn đoán:
                        </strong>

                        ${escapeHtml(
                            item.diagnosis ||
                            "—"
                        )}

                    </div>

                </div>
            `
        ).join("");

}


function setupEvents() {

    document
        .getElementById(
            "medicalRecordForm"
        )
        .addEventListener(
            "submit",
            saveMedicalRecord
        );


    document
        .getElementById(
            "addMedicineButton"
        )
        .addEventListener(
            "click",
            () => addMedicineRow()
        );


    document
        .getElementById(
            "savePrescriptionButton"
        )
        .addEventListener(
            "click",
            savePrescription
        );


    document
        .getElementById(
            "completeAppointmentButton"
        )
        .addEventListener(
            "click",
            completeAppointment
        );


    const examinedAt =
        document.getElementById(
            "examinedAt"
        );


    if (!examinedAt.value) {

        const now =
            new Date();


        now.setMinutes(
            now.getMinutes() -
            now.getTimezoneOffset()
        );


        examinedAt.value =
            now
                .toISOString()
                .slice(
                    0,
                    16
                );

    }

}


function showExaminationAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "examinationAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );

}
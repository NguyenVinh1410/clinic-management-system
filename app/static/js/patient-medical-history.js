document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            const response =
                await apiFetch(
                    "/api/patients/me/medical_history"
                );


            const data =
                await parseApiResponse(
                    response
                );


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Không thể tải lịch sử khám."
                );

            }


            renderMedicalHistory(
                data.items
            );

        }
        catch (error) {

            console.error(error);

            showHistoryAlert(
                error.message ||
                "Không thể tải lịch sử khám.",
                "danger"
            );

        }

    }
);


function renderMedicalHistory(
    records
) {

    const container =
        document.getElementById(
            "historyList"
        );


    if (!records.length) {

        container.innerHTML = `
            <div class="content-card p-5 text-center">

                <i
                    class="bi bi-file-medical fs-1 text-secondary">
                </i>

                <h5 class="fw-bold mt-3">
                    Chưa có lịch sử khám
                </h5>

                <p class="text-secondary mb-0">
                    Bạn chưa có hồ sơ khám nào.
                </p>

            </div>
        `;

        return;

    }


    container.innerHTML =
        records
            .map(
                record => `

                    <div class="content-card mb-4">

                        <div class="p-4 border-bottom">

                            <div class="d-flex justify-content-between gap-3 flex-wrap">

                                <div>

                                    <div class="text-secondary small">

                                        ${formatDateTime(
                                            record.examined_at
                                        )}

                                    </div>

                                    <h5 class="fw-bold mb-1">

                                        ${escapeHtml(
                                            record.doctor_name
                                        )}

                                    </h5>

                                    <div class="text-secondary">

                                        ${escapeHtml(
                                            record.specialty_name
                                        )}

                                    </div>

                                </div>


                                <div>

                                    ${renderStatusBadge(
                                        "Completed"
                                    )}

                                </div>

                            </div>

                        </div>


                        <div class="p-4">

                            <div class="mb-4">

                                <div class="text-secondary small mb-1">
                                    Triệu chứng
                                </div>

                                <div>
                                    ${
                                        escapeHtml(
                                            record.symptoms ||
                                            "Không ghi nhận"
                                        )
                                    }
                                </div>

                            </div>


                            <div class="mb-4">

                                <div class="text-secondary small mb-1">
                                    Chẩn đoán
                                </div>

                                <div class="fw-semibold">

                                    ${escapeHtml(
                                        record.diagnosis
                                    )}

                                </div>

                            </div>


                            <div>

                                <div class="text-secondary small mb-1">
                                    Ghi chú
                                </div>

                                <div>

                                    ${
                                        escapeHtml(
                                            record.note ||
                                            "Không có"
                                        )
                                    }

                                </div>

                            </div>

                        </div>

                    </div>

                `
            )
            .join("");

}


function showHistoryAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "historyAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );

}


function escapeHtml(
    value
) {

    return String(
        value ?? ""
    )
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}
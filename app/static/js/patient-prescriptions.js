let patientPrescriptions = [];


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {
            window.location.href = "/login";
            return;
        }

        try {

            await loadPatientPrescriptions();

        }
        catch (error) {

            console.error(
                error
            );

            showPrescriptionAlert(
                error.message ||
                "Không thể tải đơn thuốc.",
                "danger"
            );

        }

    }
);


async function loadPatientPrescriptions() {

    const response =
        await apiFetch(
            "/api/prescription/my"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải đơn thuốc."
        );

    }


    patientPrescriptions =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderPrescriptions();

}


function renderPrescriptions() {

    const container =
        document.getElementById(
            "prescriptionList"
        );


    if (
        !patientPrescriptions.length
    ) {

        container.innerHTML = `
            <div
                class="content-card
                       p-5
                       text-center">

                <i
                    class="bi
                           bi-capsule
                           fs-1
                           text-secondary">
                </i>

                <h5
                    class="fw-bold mt-3">

                    Chưa có đơn thuốc

                </h5>

                <p
                    class="text-secondary mb-0">

                    Bạn chưa có đơn thuốc nào.

                </p>

            </div>
        `;

        return;

    }


    container.innerHTML =
        patientPrescriptions
            .map(
                prescription =>
                    renderPrescriptionCard(
                        prescription
                    )
            )
            .join("");

}


function renderPrescriptionCard(
    prescription
) {

    const total =
        prescription.details.reduce(
            (
                sum,
                detail
            ) => {

                return (
                    sum +
                    Number(
                        detail.line_total ||
                        (
                            detail.medicine.price *
                            detail.quantity
                        )
                    )
                );

            },
            0
        );


    return `
        <div
            class="content-card mb-4">

            <div
                class="p-4 border-bottom">

                <div
                    class="d-flex
                           justify-content-between
                           align-items-start
                           gap-3
                           flex-wrap">

                    <div>

                        <h5
                            class="fw-bold mb-1">

                            Đơn thuốc
                            #${prescription.prescription_id}

                        </h5>

                        <div
                            class="small text-secondary">

                            Ngày kê:
                            ${formatDateTime(
                                prescription.created_at
                            )}

                        </div>

                    </div>

                </div>

            </div>


            <div class="table-responsive">

                <table
                    class="table
                           align-middle
                           mb-0">

                    <thead>

                        <tr>

                            <th>
                                Thuốc
                            </th>

                            <th>
                                Đơn vị
                            </th>

                            <th>
                                Đơn giá
                            </th>

                            <th>
                                Số lượng
                            </th>

                            <th>
                                Thành tiền
                            </th>

                            <th>
                                Liều dùng
                            </th>

                            <th>
                                Cách dùng
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        ${
                            prescription.details
                                .map(
                                    detail => {

                                        const medicine =
                                            detail.medicine;


                                        return `
                                            <tr>

                                                <td>

                                                    <div
                                                        class="fw-semibold">

                                                        ${escapeHtml(
                                                            medicine.name
                                                        )}

                                                    </div>

                                                </td>


                                                <td>

                                                    ${escapeHtml(
                                                        medicine.unit
                                                    )}

                                                </td>


                                                <td>

                                                    ${formatCurrency(
                                                        medicine.price
                                                    )}

                                                </td>


                                                <td>

                                                    ${detail.quantity}

                                                </td>


                                                <td
                                                    class="fw-semibold">

                                                    ${formatCurrency(
                                                        detail.line_total
                                                    )}

                                                </td>


                                                <td>

                                                    ${escapeHtml(
                                                        detail.dosage
                                                    )}

                                                </td>


                                                <td>

                                                    ${escapeHtml(
                                                        detail.usage_note ||
                                                        "—"
                                                    )}

                                                </td>

                                            </tr>
                                        `;

                                    }
                                )
                                .join("")
                        }

                    </tbody>

                </table>

            </div>


            <div
                class="p-4
                       border-top
                       text-end">

                <span
                    class="text-secondary
                           me-2">

                    Tổng tiền thuốc:

                </span>

                <strong
                    class="fs-5">

                    ${formatCurrency(
                        total
                    )}

                </strong>

            </div>

        </div>
    `;
}


function showPrescriptionAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "prescriptionAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );

}
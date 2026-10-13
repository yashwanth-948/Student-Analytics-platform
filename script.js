"use strict";

// -----------------------------------------
// 1. Sample data
// -----------------------------------------

const STORAGE_KEY = "smartCampusStudents";

const sampleStudents = [
    {
        roll: "CSE001", name: "Rahul Kumar", department: "CSE",
        cgpa: 5.8, attendance: 62, lms: 55, engagement: 50,
        placement: 35, skills: 40, feedback: 60,
        backlogs: 3, aptitude: 35, coding: 30
    },
    {
        roll: "CSE002", name: "Priya Sharma", department: "CSE",
        cgpa: 9.1, attendance: 94, lms: 95, engagement: 90,
        placement: 88, skills: 92, feedback: 90,
        backlogs: 0, aptitude: 90, coding: 92
    },
    {
        roll: "ECE001", name: "Arjun Reddy", department: "ECE",
        cgpa: 7.2, attendance: 78, lms: 75, engagement: 72,
        placement: 48, skills: 45, feedback: 75,
        backlogs: 1, aptitude: 55, coding: 50
    },
    {
        roll: "IT001", name: "Sneha Rao", department: "IT",
        cgpa: 8.4, attendance: 88, lms: 85, engagement: 86,
        placement: 80, skills: 84, feedback: 88,
        backlogs: 0, aptitude: 82, coding: 85
    },
    {
        roll: "EEE001", name: "Kiran Kumar", department: "EEE",
        cgpa: 6.7, attendance: 82, lms: 68, engagement: 65,
        placement: 58, skills: 60, feedback: 72,
        backlogs: 0, aptitude: 55, coding: 48
    },
    {
        roll: "MECH001", name: "Vikram Singh", department: "Mechanical",
        cgpa: 7.8, attendance: 90, lms: 80, engagement: 78,
        placement: 72, skills: 75, feedback: 82,
        backlogs: 0, aptitude: 70, coding: 68
    },
    {
        roll: "CIVIL001", name: "Ananya Das", department: "Civil",
        cgpa: 6.1, attendance: 70, lms: 60, engagement: 58,
        placement: 45, skills: 42, feedback: 65,
        backlogs: 2, aptitude: 38, coding: 35
    },
    {
        roll: "IT002", name: "Meghana Reddy", department: "IT",
        cgpa: 8.8, attendance: 92, lms: 90, engagement: 88,
        placement: 85, skills: 87, feedback: 90,
        backlogs: 0, aptitude: 86, coding: 89
    }
];

// -----------------------------------------
// 2. Load saved data or sample data
// -----------------------------------------

function loadStudents() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);

        if (saved !== null) {
            const parsed = JSON.parse(saved);

            if (Array.isArray(parsed)) {
                return parsed;
            }
        }
    } catch (error) {
        console.error("Could not load saved students:", error);
    }

    return sampleStudents.map(student => ({ ...student }));
}

let students = loadStudents();

// -----------------------------------------
// 3. Calculate score and risk
// -----------------------------------------

function calculateSuccessScore(student) {
    const score =
        (Number(student.cgpa) / 10) * 30 +
        (Number(student.attendance) / 100) * 20 +
        (Number(student.lms) / 100) * 10 +
        (Number(student.engagement) / 100) * 10 +
        (Number(student.placement) / 100) * 15 +
        (Number(student.skills) / 100) * 10 +
        (Number(student.feedback) / 100) * 5;

    return Math.round(score * 10) / 10;
}

function getRiskDetails(student) {
    const reasons = [];

    if (Number(student.cgpa) < 6.5) {
        reasons.push("Low CGPA");
    }

    if (Number(student.attendance) < 75) {
        reasons.push("Low attendance");
    }

    if (Number(student.backlogs) > 0) {
        reasons.push("Pending backlogs");
    }

    if (Number(student.placement) < 50) {
        reasons.push("Low placement readiness");
    }

    if (Number(student.skills) < 50) {
        reasons.push("Skills improvement needed");
    }

    if (Number(student.aptitude) < 40) {
        reasons.push("Low aptitude score");
    }

    if (Number(student.coding) < 40) {
        reasons.push("Low coding score");
    }

    let risk = "Low";

    if (reasons.length >= 2) {
        risk = "High";
    } else if (reasons.length === 1) {
        risk = "Medium";
    }

    return { risk, reasons };
}

function enrichStudent(student) {
    const details = getRiskDetails(student);

    return {
        ...student,
        score: calculateSuccessScore(student),
        risk: details.risk,
        reasons: details.reasons
    };
}

// -----------------------------------------
// 4. Safe HTML display helper
// -----------------------------------------

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];
    });
}

// -----------------------------------------
// 5. Dashboard summary cards
// -----------------------------------------

function updateStatistics() {
    const data = students.map(enrichStudent);

    const total = data.length;

    const averageScore = total
        ? data.reduce((sum, student) => sum + student.score, 0) / total
        : 0;

    const highRisk = data.filter(student => student.risk === "High").length;

    const averageAttendance = total
        ? data.reduce(
            (sum, student) => sum + Number(student.attendance), 0
        ) / total
        : 0;

    document.getElementById("totalStudents").textContent = total;

    document.getElementById("averageScore").textContent =
        averageScore.toFixed(1) + "%";

    document.getElementById("highRiskStudents").textContent = highRisk;

    document.getElementById("averageAttendance").textContent =
        averageAttendance.toFixed(1) + "%";
}

// -----------------------------------------
// 6. Student table and filters
// -----------------------------------------

function renderStudentTable() {
    const tbody = document.getElementById("studentTableBody");
    const search = document.getElementById("searchInput")
        .value.trim().toLowerCase();

    const riskFilter = document.getElementById("riskFilter").value;

    const filteredStudents = students
        .map(enrichStudent)
        .filter(student => {
            const searchableText = [
                student.name,
                student.roll,
                student.department
            ].join(" ").toLowerCase();

            const matchesSearch = searchableText.includes(search);
            const matchesRisk =
                riskFilter === "All" || student.risk === riskFilter;

            return matchesSearch && matchesRisk;
        });

    tbody.innerHTML = filteredStudents.map(student => {
        const riskClass = "risk-" + student.risk.toLowerCase();

        const insights = student.reasons.length
            ? student.reasons.join(", ")
            : "No current risk flags";

        return `
            <tr>
                <td>
                    <span class="student-name">
                        ${escapeHTML(student.name)}
                    </span>
                    <span class="sub-text">
                        ${escapeHTML(student.roll)}
                    </span>
                </td>
                <td>${escapeHTML(student.department)}</td>
                <td>${Number(student.cgpa).toFixed(1)}</td>
                <td>${Number(student.attendance)}%</td>
                <td><strong>${student.score.toFixed(1)}%</strong></td>
                <td>
                    <span class="risk-badge ${riskClass}">
                        ${escapeHTML(student.risk)}
                    </span>
                </td>
                <td class="insight">${escapeHTML(insights)}</td>
            </tr>
        `;
    }).join("");

    document.getElementById("emptyMessage").hidden =
        filteredStudents.length !== 0;
}

// -----------------------------------------
// 7. Chart references
// -----------------------------------------

let riskChartInstance = null;
let departmentChartInstance = null;

// -----------------------------------------
// 8. Student Risk Distribution chart
// -----------------------------------------

function updateRiskChart(data) {
    const canvas = document.getElementById("riskChart");

    if (!canvas) {
        console.error('Missing canvas: id="riskChart"');
        return;
    }

    if (typeof Chart === "undefined") {
        console.error(
            "Chart.js is unavailable. Check your internet connection and CDN."
        );
        return;
    }

    const counts = { High: 0, Medium: 0, Low: 0 };

    data.forEach(student => {
        counts[student.risk]++;
    });

    if (riskChartInstance) {
        riskChartInstance.destroy();
    }

    riskChartInstance = new Chart(canvas, {
        type: "doughnut",

        data: {
            labels: ["High Risk", "Medium Risk", "Low Risk"],

            datasets: [{
                data: [counts.High, counts.Medium, counts.Low],
                backgroundColor: ["#ef4444", "#f59e0b", "#10b981"],
                hoverOffset: 8,
                borderWidth: 2,
                borderColor: "#ffffff"
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "62%",

            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },

                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data
                                .reduce((sum, value) => sum + value, 0);

                            const percentage = total
                                ? ((context.raw / total) * 100).toFixed(1)
                                : "0.0";

                            return `${context.label}: ${context.raw} students (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// -----------------------------------------
// 9. Department Success Scores chart
// -----------------------------------------

function updateDepartmentChart(data) {
    const canvas = document.getElementById("departmentChart");

    if (!canvas) {
        console.error('Missing canvas: id="departmentChart"');
        return;
    }

    if (typeof Chart === "undefined") {
        console.error("Chart.js is unavailable.");
        return;
    }

    const departmentTotals = {};

    data.forEach(student => {
        const department = student.department || "Unknown";

        if (!departmentTotals[department]) {
            departmentTotals[department] = {
                total: 0,
                count: 0
            };
        }

        departmentTotals[department].total += student.score;
        departmentTotals[department].count++;
    });

    const departments = Object.keys(departmentTotals).sort();

    const averages = departments.map(department => {
        const item = departmentTotals[department];

        return Math.round((item.total / item.count) * 10) / 10;
    });

    if (departmentChartInstance) {
        departmentChartInstance.destroy();
    }

    departmentChartInstance = new Chart(canvas, {
        type: "bar",

        data: {
            labels: departments,

            datasets: [{
                label: "Average Success Score",
                data: averages,
                backgroundColor: "#14b8a6",
                hoverBackgroundColor: "#0f766e",
                borderRadius: 6,
                maxBarThickness: 48
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            scales: {
                x: {
                    grid: { display: false }
                },

                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 100,

                    ticks: {
                        stepSize: 20,
                        callback: value => value + "%"
                    },

                    title: {
                        display: true,
                        text: "Average Success Score"
                    }
                }
            },

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    callbacks: {
                        label: context =>
                            "Average score: " + context.raw + "%"
                    }
                }
            }
        }
    });
}

// -----------------------------------------
// 10. Refresh all dashboard components
// -----------------------------------------

function refreshDashboard() {
    const data = students.map(enrichStudent);

    updateStatistics();
    renderStudentTable();
    updateRiskChart(data);
    updateDepartmentChart(data);
}

// -----------------------------------------
// 11. Save student data in browser
// -----------------------------------------

function saveStudents() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(students));
        return true;
    } catch (error) {
        console.error("Could not save student data:", error);
        return false;
    }
}

// -----------------------------------------
// 12. Add student form
// -----------------------------------------

document.getElementById("studentForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const getValue = name => formData.get(name);

    const newStudent = {
        name: String(getValue("name")).trim(),
        roll: String(getValue("roll")).trim(),
        department: String(getValue("department")),
        cgpa: Number(getValue("cgpa")),
        attendance: Number(getValue("attendance")),
        lms: Number(getValue("lms")),
        engagement: Number(getValue("engagement")),
        placement: Number(getValue("placement")),
        skills: Number(getValue("skills")),
        feedback: Number(getValue("feedback")),
        backlogs: Number(getValue("backlogs")),
        aptitude: Number(getValue("aptitude")),
        coding: Number(getValue("coding"))
    };

    const percentageFields = [
        "attendance", "lms", "engagement", "placement",
        "skills", "feedback", "aptitude", "coding"
    ];

    const validCGPA =
        Number.isFinite(newStudent.cgpa) &&
        newStudent.cgpa >= 0 && newStudent.cgpa <= 10;

    const validPercentages = percentageFields.every(field =>
        Number.isFinite(newStudent[field]) &&
        newStudent[field] >= 0 &&
        newStudent[field] <= 100
    );

    const validBacklogs =
        Number.isInteger(newStudent.backlogs) &&
        newStudent.backlogs >= 0 &&
        newStudent.backlogs <= 30;

    const message = document.getElementById("formMessage");

    if (!newStudent.name || !newStudent.roll) {
        message.textContent = "Enter both the student name and roll number.";
        return;
    }

    if (!validCGPA || !validPercentages || !validBacklogs) {
        message.textContent =
            "Check your values. CGPA must be 0–10, percentages 0–100, and backlogs 0–30.";
        return;
    }

    const duplicate = students.some(student =>
        student.roll.toLowerCase() === newStudent.roll.toLowerCase()
    );

    if (duplicate) {
        message.textContent = "That roll number already exists.";
        return;
    }

    students.push(newStudent);

    const saved = saveStudents();

    refreshDashboard();

    message.textContent = saved
        ? "Student added and dashboard updated successfully."
        : "Student added for this session, but browser storage failed.";

    form.reset();
});

// -----------------------------------------
// 13. Search and risk filter events
// -----------------------------------------

document.getElementById("searchInput")
    .addEventListener("input", renderStudentTable);

document.getElementById("riskFilter")
    .addEventListener("change", renderStudentTable);

// -----------------------------------------
// 14. Export student records to CSV
// -----------------------------------------

document.getElementById("exportBtn").addEventListener("click", function() {
    const data = students.map(enrichStudent);

    const headers = [
        "Roll Number", "Name", "Department", "CGPA", "Attendance",
        "LMS Completion", "Engagement", "Placement Readiness",
        "Skills", "Feedback", "Backlogs", "Aptitude", "Coding",
        "Success Score", "Risk Level", "Risk Insights"
    ];

    const rows = data.map(student => [
        student.roll,
        student.name,
        student.department,
        student.cgpa,
        student.attendance,
        student.lms,
        student.engagement,
        student.placement,
        student.skills,
        student.feedback,
        student.backlogs,
        student.aptitude,
        student.coding,
        student.score,
        student.risk,
        student.reasons.join("; ")
    ]);

    function csvCell(value) {
        let text = String(value ?? "");

        // Reduce the risk of spreadsheet formula injection.
        if (/^[\s]*[=+\-@]/.test(text)) {
            text = "'" + text;
        }

        return '"' + text.replace(/"/g, '""') + '"';
    }

    const csvContent = [headers, ...rows]
        .map(row => row.map(csvCell).join(","))
        .join("\r\n");

    const blob = new Blob(["\uFEFF" + csvContent], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "student-analytics.csv";

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);
});

// -----------------------------------------
// 15. Sidebar active link
// -----------------------------------------

document.querySelectorAll(".nav-link").forEach(link => {
    link.addEventListener("click", function() {
        document.querySelectorAll(".nav-link").forEach(item => {
            item.classList.remove("active");
        });

        this.classList.add("active");
    });
});

// -----------------------------------------
// 16. Start dashboard after page loads
// -----------------------------------------

document.addEventListener("DOMContentLoaded", function() {
    refreshDashboard();
});
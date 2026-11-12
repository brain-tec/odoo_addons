/** @odoo-module **/

import { loadBundle } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { getColor, hexToRGBA } from "@web/core/colors/colors";
import { cookie } from "@web/core/browser/cookie";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, onWillStart, useEffect, useRef } from "@odoo/owl";

/**
 * Weekly evolution of the webservice calls and errors (two series on one line chart).
 * The field value is a JSON with `labels`, `calls` and `errors` lists.
 */
export class WebserviceDashboardGraphField extends Component {
    static template = "smile_webservice.WebserviceDashboardGraphField";
    static props = { ...standardFieldProps };

    setup() {
        this.chart = null;
        this.canvasRef = useRef("canvas");

        onWillStart(async () => await loadBundle("web.chartjs_lib"));

        useEffect(() => {
            this.renderChart();
            return () => this.chart?.destroy();
        });
    }

    get data() {
        return JSON.parse(this.props.record.data[this.props.name] || "{}");
    }

    renderChart() {
        this.chart?.destroy();
        const data = this.data;
        const colorScheme = cookie.get("color_scheme");
        const callsColor = getColor(0, colorScheme);
        const errorsColor = getColor(6, colorScheme);
        this.chart = new Chart(this.canvasRef.el, {
            type: "line",
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: data.calls_label,
                        data: data.calls || [],
                        borderColor: callsColor,
                        backgroundColor: hexToRGBA(callsColor, 0.15),
                        fill: "start",
                        borderWidth: 2,
                        pointRadius: 2,
                    },
                    {
                        label: data.errors_label,
                        data: data.errors || [],
                        borderColor: errorsColor,
                        backgroundColor: errorsColor,
                        borderDash: [5, 4],
                        borderWidth: 2,
                        pointRadius: 2,
                        pointStyle: "rectRot",
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { boxWidth: 12, boxHeight: 2, usePointStyle: false },
                    },
                    tooltip: { caretSize: 0 },
                },
                scales: {
                    x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 8 } },
                    y: { beginAtZero: true, ticks: { precision: 0, maxTicksLimit: 4 } },
                },
                elements: { line: { tension: 0.25 } },
            },
        });
    }
}

export const webserviceDashboardGraphField = {
    component: WebserviceDashboardGraphField,
    supportedTypes: ["text"],
};

registry.category("fields").add("webservice_dashboard_graph", webserviceDashboardGraphField);

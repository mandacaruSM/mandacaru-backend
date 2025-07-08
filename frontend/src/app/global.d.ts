declare module "recharts" {
  import * as React from "react";
  import {
    BarChart as _BarChart,
    Bar as _Bar,
    XAxis as _XAxis,
    YAxis as _YAxis,
    Tooltip as _Tooltip,
    ResponsiveContainer as _ResponsiveContainer
  } from "recharts";

  export const BarChart: typeof _BarChart;
  export const Bar: typeof _Bar;
  export const XAxis: typeof _XAxis;
  export const YAxis: typeof _YAxis;
  export const Tooltip: typeof _Tooltip;
  export const ResponsiveContainer: typeof _ResponsiveContainer;
}

import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";
import "./Statistics.css";
import API_BASE_URL from "../../utils/config";

const Statistics = () => {
  const [graph, setGraph] = useState("tomato_annual");
  const [plotData, setPlotData] = useState(null);
  const [graphTitle, setGraphTitle] = useState("");
  const [years] = useState(Array.from({ length: 11 }, (_, i) => 2016 + i));
  const [selectedYears, setSelectedYears] = useState({
    tomato_year: 2025,
    strawberry_year: 2025,
    tomato_year_retail: 2025,
    strawberry_year_retail: 2025,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchGraphData();
  }, [graph, selectedYears]);

  const fetchGraphData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        graph: graph,
        ...selectedYears,
      });
      const response = await fetch(`${API_BASE_URL}/api/statistics?${params}`);
      if (!response.ok) throw new Error("API 오류");
      const data = await response.json();
      setPlotData(JSON.parse(data.plot_json));
      setGraphTitle(data.graph_title);
    } catch (error) {
      setError("데이터를 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleYearChange = (name, value) => {
    setSelectedYears((prev) => ({
      ...prev,
      [name]: parseInt(value),
    }));
  };

  const renderYearSelect = () => {
    const yearSelectConfig = {
      tomato_monthly_wholesale: {
        name: "tomato_year",
        label: "토마토 월 선택 연도:",
      },
      strawberry_monthly_wholesale: {
        name: "strawberry_year",
        label: "딸기 월 선택 연도:",
      },
      tomato_monthly_retail: {
        name: "tomato_year_retail",
        label: "토마토 월 선택 연도:",
      },
      strawberry_monthly_retail: {
        name: "strawberry_year_retail",
        label: "딸기 월 선택 연도:",
      },
    };

    const config = yearSelectConfig[graph];
    if (!config) return null;

    return (
      <div className="year-select-form">
        <label htmlFor={config.name}>{config.label}</label>
        <select
          id={config.name}
          value={selectedYears[config.name]}
          onChange={(e) => handleYearChange(config.name, e.target.value)}
        >
          {years.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>
    );
  };

  return (
    <div className="statistics-container">
      <div className="sidebar">
        <h2>그래프 선택</h2>
        <a
          href="#"
          className={graph === "tomato_annual" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            setGraph("tomato_annual");
          }}
        >
          토마토 연간 시세
        </a>
        <a
          href="#"
          className={graph === "strawberry_annual" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            setGraph("strawberry_annual");
          }}
        >
          딸기 연간 시세
        </a>
        <a
          href="#"
          className={graph === "tomato_monthly_wholesale" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            setGraph("tomato_monthly_wholesale");
          }}
        >
          토마토 월간 도매
        </a>
        <a
          href="#"
          className={graph === "strawberry_monthly_wholesale" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            setGraph("strawberry_monthly_wholesale");
          }}
        >
          딸기 월간 도매
        </a>
        <a
          href="#"
          className={graph === "tomato_monthly_retail" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            setGraph("tomato_monthly_retail");
          }}
        >
          토마토 월간 소매
        </a>
        <a
          href="#"
          className={graph === "strawberry_monthly_retail" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            setGraph("strawberry_monthly_retail");
          }}
        >
          딸기 월간 소매
        </a>
      </div>
      <div className="statistics-content">
        <div className="graph-title">{graphTitle}</div>
        {renderYearSelect()}
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>데이터를 불러오는 중...</p>
          </div>
        )}
        {error && (
          <div className="error-container">
            <div className="error-icon">⚠️</div>
            <p>{error}</p>
          </div>
        )}
        {plotData && !loading && !error && (
          <Plot
            data={plotData.data}
            layout={{
              ...plotData.layout,
              autosize: true,
              responsive: true,
              font: {
                family:
                  '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                size: 13,
                color: "#2c3e50",
              },
              plot_bgcolor: "#ffffff",
              paper_bgcolor: "#ffffff",
              margin: { l: 60, r: 40, t: 60, b: 60 },
            }}
            style={{ width: "100%", height: "600px" }}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ["pan2d", "lasso2d", "select2d"],
            }}
          />
        )}
      </div>
    </div>
  );
};

export default Statistics;

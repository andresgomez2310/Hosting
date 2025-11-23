import React, { useState } from "react";
import Sidebar from "./Sidebar";
import "../styles.css";

export default function Layout({ children }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="layout">
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

      <main className={`main-content ${collapsed ? "collapsed" : ""}`}>
        {children}
      </main>
    </div>
  );
}

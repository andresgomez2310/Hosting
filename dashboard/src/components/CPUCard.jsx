export default function CPUCard({ data }) {
  return (
    <div style={{ border: "1px solid #999", padding: "15px", marginTop: "20px" }}>
      <h2>Uso del CPU</h2>

      <p><b>Modelo:</b> {data.model}</p>
      <p><b>Núcleos:</b> {data.cores}</p>
      <p><b>Uso actual:</b> {data.usage}%</p>
    </div>
  );
}

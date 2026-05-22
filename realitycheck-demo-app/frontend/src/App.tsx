import { loadDashboard } from "./api";

export function App() {
  void loadDashboard();
  return <main>Acme Ops Portal</main>;
}

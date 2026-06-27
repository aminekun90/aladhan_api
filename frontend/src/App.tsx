import { HomePage } from "@/pages/HomePage";
import { theme } from "@/theme";
import { ToastContainer } from "@aminekun90/react-toast";
import { CssBaseline, ThemeProvider } from "@mui/material";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <ToastContainer />
      <CssBaseline />
      <HomePage />
    </ThemeProvider>
  );
}

export default App;

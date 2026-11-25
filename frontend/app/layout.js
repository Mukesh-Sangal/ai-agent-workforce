import "./globals.css";

export const metadata = {
  title: "AI Agent Workforce",
  description: "Understand tasks before planning and execution.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
 
);
}
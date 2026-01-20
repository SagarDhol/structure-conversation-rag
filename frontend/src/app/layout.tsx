import type { Metadata } from "next";
import "../../styles/theme.css";
import styles from "./layout.module.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Conversational RAG",
  description: "Production-ready Retrieval Augmented Generation System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Roboto:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div className={styles.app}>
          <nav className={styles.nav}>
            <div className={styles.navContent}>
              <Link href="/" className={styles.logo}>
                <span className={styles.logoIcon}>🧠</span>
                <span className={styles.logoText}>RAG Assistant</span>
              </Link>
              <div className={styles.navLinks}>
                <Link href="/" className={styles.navLink}>
                  Chat
                </Link>
                <Link href="/documents" className={styles.navLink}>
                  Documents
                </Link>
              </div>
            </div>
          </nav>
          <main className={styles.main}>{children}</main>
        </div>
      </body>
    </html>
  );
}

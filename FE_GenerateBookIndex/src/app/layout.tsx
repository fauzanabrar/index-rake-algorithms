"use client";
import './globals.css'
import 'react-toastify/dist/ReactToastify.css';

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body>
                <div className="page">
                    {children}
                </div>
            </body>
        </html>
    )
}

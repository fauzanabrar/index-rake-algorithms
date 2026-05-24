"use client";
import FileIcon from "@/Icons/FileIcon";
import PdfIcon from "@/Icons/PdfIcon";
import TriangleIcon from "@/Icons/TriangleIcon";
import UploadIcon from "@/Icons/UploadIcon";
import XIcon from "@/Icons/XIcon";
import LoadingButton from "@/components/LoadingButton";
import axios from "axios";
import { useEffect, useState } from "react";
import React from "react";

const page = () => {
    const [file, setFile] = useState<any>();
    const [jsonFile, setJsonFile] = useState<any>();
    const [judul, setJudul] = useState<string>("");
    const [draggingOver, setDraggingOver] = useState<boolean>(false)
    const [XOver, setXOver] = useState<boolean>(false);

    const handleDrop = (ev: any) => {
        console.log("File(s) dropped");

        // Prevent default behavior (Prevent file from being opened)
        ev.preventDefault();
        setFile(ev.dataTransfer.files[0])
        setDraggingOver(false);
    }

    const handleDragOver = (e: any) => {
        console.log("File in dropzone");
        setDraggingOver(true);
        e.preventDefault();
    }

    /* --- Hover display keterangan nomor VS urutan halaman ------ */
    const [hoverNomor, setHoverNomor] = useState<boolean>(false);
    const [hoverUrutan, setHoverUrutan] = useState<boolean>(false);

    /* --- Form ------------------ */
    const [terlangkah, setTerlangkah] = useState<boolean|undefined>();
    const [stepOnMiddle, setStepOnMiddle] = useState<boolean|undefined>();

    // without JSON input:
    const [firstPage, setFirstPage] = useState<number>();
    const [lastPage, setLastPage] = useState<number>();
    const [urutanPertama, setUrutanPertama] = useState<number>();

    const [loading, setLoading] = useState<boolean>(false);
    const processTheBook = async () => {
        setLoading(true);

        const fileName = `Index ${judul}.docx`
        const formData = new FormData();
        formData.append("filePdf", file);
        formData.append("judul", judul);
        formData.append("adaJSON", "1");
        if (terlangkah || stepOnMiddle) {
            formData.append("fileJson", jsonFile);
        } else {
            const generatedJSONtext = JSON.stringify([
                {"f": firstPage, "l": lastPage, "d": (urutanPertama! - firstPage!)}
            ]);
            const encoder = new TextEncoder();
            const binaryData = encoder.encode(generatedJSONtext);
            formData.append("fileJson", new Blob([binaryData], { type: 'application/octet-stream' }));
        }

        try {
            const response = await axios({
                url: "http://localhost:1313/generate-rake",
                method: "POST",
                responseType: "blob",
                data: formData
            })
            const blob = new Blob([response.data], { type: response.headers['content-type'] });
        
            // Create a download link
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', fileName);
    
            // Append the link to the document and trigger the click event
            document.body.appendChild(link);
            link.click();
    
            // Remove the link from the document
            document.body.removeChild(link);
        } catch (error) {
            console.error(error);
            alert("Terjadi error pada saat generate file");
        } finally {
            setLoading(false);
        }
    }

    const cancelHandler = () => {
        setFile(undefined);
        setJudul("");
        setTerlangkah(undefined);
        setStepOnMiddle(undefined);
        setJsonFile(undefined);
        setFirstPage(undefined);
        setLastPage(undefined);
        setUrutanPertama(undefined);
    }

    const checkFormComplete = () => {
        let value = false;

        // basic requirement
        if (!file || !judul || terlangkah===undefined || stepOnMiddle===undefined) {
            value = false;
        } else {
            // without JSON
            if (terlangkah===false && stepOnMiddle===false) {
                if (firstPage===undefined || lastPage===undefined || urutanPertama===undefined) {
                    value = false;
                } else {
                    value = true;
                }
            } 
            // with JSON
            else {
                if (!jsonFile) {
                    value = false;
                } else {
                    value = true;
                }
            }
        }

        return value;
    }

    useEffect(() => {
        if (file) {
            const pdf = window.URL.createObjectURL(file);
            const object = document.querySelector("object");
            if (object?.data) object.data = pdf;
        }
    }, [file])

    return (
        <div className="wrapper">
            <div className="header">
                Implementasi Algoritma <span>Rapid Automatic Keyword Extraction (RAKE)</span> pada Pembuatan Indeks Buku
            </div>
            <div className="content">
                {!file && <label className={`dropPdf ${draggingOver ? "dragging" : ""}`} onDrop={handleDrop} onDragOver={handleDragOver} onClick={(e) => console.log(e)}>
                    <PdfIcon color={draggingOver ? "#1300F3" : "#0070F3"} />
                    <input type="file" accept="application/pdf" className="pdfInput" onChange={(e) => {
                        if (!e.target.files) return;
                        setFile(e.target.files[0]);
                    }} />
                    <div>Drop file PDF buku atau <span>browse</span></div>
                </label>}

                {file && 
                    <div className="havePdf">
                        <object className="pdf-view" data="" width="100%" height="400px"/>

                        <div className="form">
                            <div className="box">
                                <div className="topbar">
                                    <div className="filename">
                                        <FileIcon/> <div>{file?.name?.length > 40 ? `${file?.name?.substring(0,40)}....pdf` : file?.name}</div>
                                    </div>
                                    <div className="cancel" onMouseOver={() => setXOver(true)} onMouseLeave={() => setXOver(false)} onClick={cancelHandler}><XIcon color={XOver ? "#ff0000" : "#D41818"} /></div>
                                </div>
                                <div className="fields">
                                    <div className="row">
                                        <label htmlFor="judulBuku">Judul Buku</label>
                                        <input type="text" id="judulBuku" className="input" value={judul} onChange={e => setJudul(e.target.value)} />
                                    </div>
                                    <div className="row">
                                        <label className="label_lihe">Apakah ada nomor halaman yang terlangkah?</label>
                                        <div className="onerow">
                                            <div className="radio">
                                                <input type="radio" name="terlangkah" value="ya" id="ya" onChange={() => setTerlangkah(true)} checked={terlangkah===true} />
                                                <label htmlFor="ya">Ya</label>
                                            </div>
                                            <div className="radio">
                                                <input type="radio" name="terlangkah" value="tidak" id="tidak" onChange={() => setTerlangkah(false)} checked={terlangkah===false} />
                                                <label htmlFor="tidak">Tidak</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <label className="label_lihe">Apakah ada halaman tengah yang tidak ingin diindeks?</label>
                                        <div className="onerow">
                                            <div className="radio">
                                                <input type="radio" name="stepOnMiddle" value="ya" id="ya_" onChange={() => setStepOnMiddle(true)} checked={stepOnMiddle===true} />
                                                <label htmlFor="ya_">Ya</label>
                                            </div>
                                            <div className="radio">
                                                <input type="radio" name="stepOnMiddle" value="tidak" id="tidak_" onChange={() => setStepOnMiddle(false)} checked={stepOnMiddle===false} />
                                                <label htmlFor="tidak_">Tidak</label>
                                            </div>
                                        </div>
                                    </div>
                                    {(terlangkah!==undefined && stepOnMiddle!==undefined) ?
                                        terlangkah===false && stepOnMiddle===false ?
                                            <>
                                                <div className="row" onMouseOver={() => setHoverNomor(true)} onMouseLeave={() => setHoverNomor(false)}>
                                                    <label>Nomor halaman yang ingin dibuatkan indeks</label>
                                                    <div className="halamanInp">
                                                        <input type="number" className="input" value={firstPage} onChange={e => setFirstPage(Number(e.target.value))} />
                                                        <div>-</div>
                                                        <input type="number" className="input" value={lastPage} onChange={e => setLastPage(Number(e.target.value))}/>
                                                    </div>
                                                    {
                                                        hoverNomor ? 
                                                        <div className="tooltip">
                                                            <div className="text">Nomor halaman adalah nomor yang diberikan pada suatu halaman oleh penulis</div>
                                                            <TriangleIcon />
                                                        </div> : null
                                                    }
                                                </div>
                                                <div className="row" onMouseOver={() => setHoverUrutan(true)} onMouseLeave={() => setHoverUrutan(false)}>
                                                    <label>Urutan halaman pertama yang ingin diindeks</label>
                                                    <input type="number" className="input" value={urutanPertama} onChange={e => setUrutanPertama(Number(e.target.value))} />
                                                    {
                                                        hoverUrutan ? 
                                                        <div className="tooltip">
                                                            <div className="text">Urutan halaman mengacu pada susunan halaman dalam file (dokumen)</div>
                                                            <TriangleIcon />
                                                        </div> : null
                                                    }
                                                </div>
                                            </>
                                        :
                                            <div className="row">
                                                <label htmlFor="jsonfile" className="label_lihe">Unggah JSON file berisi range halaman tiap bab/section dan selisih nomor halaman yang dilabeli dan urutan halaman keseluruhan</label>
                                                <a href="/halaman.json" download="halaman.json" className="linkjsonformat">(download format JSON file)</a>
                                                <input type="file" accept="application/json" id="jsonfile" onChange={(e) => {
                                                    if (!e.target.files) return;
                                                    setJsonFile(e.target.files[0]);
                                                }} />
                                                <label htmlFor="jsonfile" className="input file">
                                                    <UploadIcon />
                                                    <div>{!jsonFile?.name ? "Unggah file json yang sudah diisi" : jsonFile.name}</div>
                                                </label>
                                            </div>
                                    : null}
                                    
                                </div>
                            </div>
                            
                            {checkFormComplete() ?
                                <button className="processBtn" onClick={processTheBook} disabled={loading}>
                                    {loading ? <LoadingButton/> : "Proses"}
                                </button>
                            : null}
                        </div>
                    </div>
                }
            </div>
        </div>
    )
}

export default page
import { useCallback, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  Image, 
  FileText, 
  X, 
  Camera, 
  Loader2,
  CheckCircle2,
  Sparkles
} from "lucide-react";
import { cn } from "@/lib/utils";

interface PrescriptionUploadProps {
  onUpload: (file: File) => void;
  isProcessing?: boolean;
}

export function PrescriptionUpload({ onUpload, isProcessing = false }: PrescriptionUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      processFile(file);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  }, []);

  const processFile = (file: File) => {
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
    onUpload(file);
  };

  const clearFile = () => {
    setPreview(null);
    setFileName(null);
  };

  return (
    <section id="upload-section" className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-10">
            <Badge variant="primary-light" className="mb-4">
              <Sparkles className="w-3 h-3 mr-1" />
              AI-Powered OCR
            </Badge>
            <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
              Upload Your Prescription
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Simply upload a photo of your prescription and our AI will extract 
              all medicine names and dosages automatically.
            </p>
          </div>

          {/* Upload Card */}
          <Card 
            variant={isDragging ? "highlight" : "elevated"} 
            className={cn(
              "relative overflow-hidden transition-all duration-300",
              isDragging && "ring-2 ring-primary ring-offset-2"
            )}
          >
            <CardContent className="p-0">
              {!preview ? (
                <label
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className="block cursor-pointer"
                >
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="sr-only"
                  />
                  <div className="p-8 md:p-12">
                    <div className="flex flex-col items-center text-center">
                      {/* Upload Icon */}
                      <div className={cn(
                        "w-20 h-20 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300",
                        isDragging 
                          ? "bg-primary text-primary-foreground scale-110" 
                          : "bg-primary-light text-primary"
                      )}>
                        <Upload className="w-10 h-10" />
                      </div>

                      {/* Text */}
                      <h3 className="text-xl font-semibold mb-2">
                        {isDragging ? "Drop your file here" : "Drag & drop your prescription"}
                      </h3>
                      <p className="text-muted-foreground mb-6">
                        or click to browse from your device
                      </p>

                      {/* Supported Formats */}
                      <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
                        {["JPG", "PNG", "HEIC", "PDF"].map((format) => (
                          <Badge key={format} variant="muted">
                            {format}
                          </Badge>
                        ))}
                      </div>

                      {/* Alternative Options */}
                      <div className="flex items-center gap-4">
                        <Button variant="outline" size="sm" className="gap-2">
                          <Camera className="w-4 h-4" />
                          Take Photo
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2">
                          <FileText className="w-4 h-4" />
                          Browse Files
                        </Button>
                      </div>
                    </div>
                  </div>
                </label>
              ) : (
                <div className="p-6">
                  {/* Preview */}
                  <div className="relative">
                    <div className="aspect-[4/3] rounded-xl overflow-hidden bg-muted relative">
                      <img 
                        src={preview} 
                        alt="Prescription preview" 
                        className="w-full h-full object-contain"
                      />
                      
                      {/* Scanning Animation */}
                      {isProcessing && (
                        <div className="absolute inset-0 bg-foreground/5">
                          <div className="absolute inset-x-0 h-1 bg-gradient-scan animate-scan" />
                        </div>
                      )}
                    </div>

                    {/* Clear Button */}
                    {!isProcessing && (
                      <Button
                        variant="secondary"
                        size="icon"
                        className="absolute top-3 right-3 rounded-full"
                        onClick={clearFile}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>

                  {/* File Info */}
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-light flex items-center justify-center">
                        <Image className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-sm truncate max-w-[200px]">
                          {fileName}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {isProcessing ? "Processing..." : "Ready to analyze"}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {isProcessing ? (
                        <Badge variant="warning-light" className="gap-1.5">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Scanning
                        </Badge>
                      ) : (
                        <Badge variant="success-light" className="gap-1.5">
                          <CheckCircle2 className="w-3 h-3" />
                          Ready
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Process Button */}
                  <Button 
                    variant="hero" 
                    className="w-full mt-6 gap-2"
                    disabled={isProcessing}
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Analyzing Prescription...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Find Best Prices
                      </>
                    )}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Security Note */}
          <p className="text-center text-xs text-muted-foreground mt-4">
            🔒 Your prescription is processed securely and never stored on our servers
          </p>
        </div>
      </div>
    </section>
  );
}

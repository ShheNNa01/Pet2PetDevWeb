import * as React from "react";
import { cn } from "../../lib/utils";

export interface TextareaProps
    extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

// Componente de Textarea con forwardRef
const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
    ({ className, ...props }, ref) => {
        return (
        <textarea
            className={cn(
            "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            className // Combina clases de Tailwind CSS
            )}
            ref={ref} // Ref de React
            {...props} // Props adicionales para el textarea
        />
        );
    }
);

// Asigna un displayName para mejorar la depuración
Textarea.displayName = "Textarea";

export { Textarea };

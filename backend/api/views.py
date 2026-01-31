from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import Dataset
from .serializers import DatasetSerializer
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
import logging

logger = logging.getLogger(__name__)

class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chemical equipment datasets.
    Provides CRUD operations and custom actions for file upload and report generation.
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Handle CSV file upload and process equipment data.
        
        Validates file, calculates statistics, and stores in database.
        Maintains only the 5 most recent uploads.
        """
        file = request.FILES.get('file')
        
        # Validation
        if not file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file.name.endswith('.csv'):
            return Response(
                {'error': 'Invalid file format. Please upload a CSV file.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Read and validate CSV
            df = pd.read_csv(file)
            
            # Validate required columns
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'Missing required columns: {", ".join(missing_columns)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate data types
            numeric_columns = ['Flowrate', 'Pressure', 'Temperature']
            for col in numeric_columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    return Response(
                        {'error': f'Column "{col}" must contain numeric values'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Calculate statistics
            total_count = len(df)
            avg_flowrate = float(df['Flowrate'].mean())
            avg_pressure = float(df['Pressure'].mean())
            avg_temperature = float(df['Temperature'].mean())
            
            # Get equipment type distribution
            equipment_types = df['Type'].value_counts().to_dict()
            
            # Reset file pointer for saving
            file.seek(0)
            
            # Create dataset record
            dataset = Dataset.objects.create(
                name=file.name,
                file=file,
                total_count=total_count,
                avg_flowrate=avg_flowrate,
                avg_pressure=avg_pressure,
                avg_temperature=avg_temperature
            )
            
            # Maintain only last 5 datasets
            old_datasets = Dataset.objects.all()[5:]
            for old in old_datasets:
                try:
                    old.file.delete(save=False)
                except Exception as e:
                    logger.warning(f"Failed to delete file for dataset {old.id}: {str(e)}")
                old.delete()
            
            logger.info(f"Dataset uploaded successfully: {file.name} (ID: {dataset.id})")
            
            # Return comprehensive response
            return Response({
                'id': dataset.id,
                'name': dataset.name,
                'uploaded_at': dataset.uploaded_at,
                'summary': {
                    'total_count': total_count,
                    'avg_flowrate': round(avg_flowrate, 2),
                    'avg_pressure': round(avg_pressure, 2),
                    'avg_temperature': round(avg_temperature, 2),
                    'equipment_types': equipment_types
                },
                'data': df.to_dict('records')
            }, status=status.HTTP_201_CREATED)
            
        except pd.errors.EmptyDataError:
            return Response(
                {'error': 'CSV file is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except pd.errors.ParserError:
            return Response(
                {'error': 'Invalid CSV format. Please check your file.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error processing CSV upload: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error processing file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def generate_report(self, request, pk=None):
        """
        Generate PDF report for a specific dataset.
        Requires authentication.
        """
        try:
            dataset = self.get_object()
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            
            # Container for PDF elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(
                f"<b>Chemical Equipment Analysis Report</b>", 
                styles['Title']
            )
            elements.append(title)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Dataset Information
            dataset_info = Paragraph(
                f"<b>Dataset:</b> {dataset.name}<br/>"
                f"<b>Upload Date:</b> {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M')}<br/>"
                f"<b>Generated:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
                styles['Normal']
            )
            elements.append(dataset_info)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Summary Statistics
            summary_title = Paragraph("<b>Summary Statistics</b>", styles['Heading2'])
            elements.append(summary_title)
            elements.append(Spacer(1, 0.2 * inch))
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Equipment', str(dataset.total_count)],
                ['Average Flowrate', f'{dataset.avg_flowrate:.2f}' if dataset.avg_flowrate else 'N/A'],
                ['Average Pressure', f'{dataset.avg_pressure:.2f}' if dataset.avg_pressure else 'N/A'],
                ['Average Temperature', f'{dataset.avg_temperature:.2f}' if dataset.avg_temperature else 'N/A']
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.5 * inch))
            
            # Footer
            footer = Paragraph(
                "<i>Generated by Chemical Equipment Parameter Visualizer</i>",
                styles['Normal']
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset.id}.pdf"'
            
            logger.info(f"PDF report generated for dataset {dataset.id} by user {request.user.username}")
            
            return response
            
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error generating report. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
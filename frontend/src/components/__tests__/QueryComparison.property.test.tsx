/**
 * Feature: text-to-sql-evaluation, Property 16: Query display completeness
 * 
 * Property-based test for QueryComparison component to ensure it displays
 * all required fields according to Requirements 6.2
 */

import { render, cleanup } from '@testing-library/react';
import * as fc from 'fast-check';
import QueryComparison from '../QueryComparison';
import { QueryComparisonData, GoldQuery } from '../../types';

// Clean up after each test
afterEach(cleanup);

// Generators for property-based testing
// Generate alphanumeric strings to avoid whitespace and special character issues
const alphanumericString = (minLength: number, maxLength: number) =>
  fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '), { minLength, maxLength });

const goldQueryArbitrary = fc.record({
  id: fc.uuid(),
  chatInput: alphanumericString(1, 100),
  sessionId: fc.option(alphanumericString(1, 50)),
  memberId: fc.option(alphanumericString(1, 50)),
  clasificacion: fc.option(alphanumericString(1, 20)),
  preguntaDescompuesta: fc.option(alphanumericString(1, 100)),
  tablasColumnasDdl: alphanumericString(1, 200),
  sqlReference: alphanumericString(1, 100),
  createdAt: fc.date()
}) as fc.Arbitrary<GoldQuery>;

const queryComparisonDataArbitrary = fc.record({
  goldQuery: goldQueryArbitrary,
  generatedSql: alphanumericString(1, 100)
}) as fc.Arbitrary<QueryComparisonData>;

describe('QueryComparison Property Tests', () => {
  /**
   * Feature: text-to-sql-evaluation, Property 16: Query display completeness
   * 
   * For any selected query, the display should include sql_reference, 
   * generated_sql, chat_input, and tablas_columnas_ddl
   * 
   * Validates: Requirements 6.2
   */
  test('Property 16: Query display completeness', () => {
    fc.assert(
      fc.property(queryComparisonDataArbitrary, (data) => {
        // Render the component with the generated data
        const { container } = render(<QueryComparison data={data} />);

        // Verify that all required fields from Requirements 6.2 are displayed
        
        // Helper function to check if text is present, accounting for whitespace normalization
        const containsText = (text: string) => {
          const normalizedText = text.trim();
          return container.textContent?.includes(normalizedText) || false;
        };
        
        // 1. Chat input should be displayed
        expect(container).toHaveTextContent('Entrada del Chat:');
        expect(containsText(data.goldQuery.chatInput)).toBe(true);

        // 2. DDL (tablas_columnas_ddl) should be displayed
        expect(container).toHaveTextContent('Esquema de Tablas (DDL):');
        expect(containsText(data.goldQuery.tablasColumnasDdl)).toBe(true);

        // 3. SQL Reference (consulta de referencia) should be displayed
        expect(container).toHaveTextContent('Consulta de Referencia (Gold)');
        expect(containsText(data.goldQuery.sqlReference)).toBe(true);

        // 4. Generated SQL (consulta generada) should be displayed
        expect(container).toHaveTextContent('Consulta Generada por IA');
        expect(containsText(data.generatedSql)).toBe(true);

        // Additional verification: ensure the component structure is correct
        // The component should show them "lado a lado" (side by side) as per requirements
        const goldSection = container.querySelector('.bg-green-50');
        const generatedSection = container.querySelector('.bg-orange-50');
        
        expect(goldSection).toBeInTheDocument();
        expect(generatedSection).toBeInTheDocument();
        
        // Clean up after this iteration
        cleanup();
      }),
      { 
        numRuns: 100,
        verbose: true
      }
    );
  });

  /**
   * Additional property test to verify optional fields are displayed when present
   */
  test('Property 16 Extension: Optional fields display when present', () => {
    fc.assert(
      fc.property(queryComparisonDataArbitrary, (data) => {
        const { container } = render(<QueryComparison data={data} />);

        // Helper function to check if text is present, accounting for whitespace normalization
        const containsText = (text: string) => {
          const normalizedText = text.trim();
          return container.textContent?.includes(normalizedText) || false;
        };

        // If preguntaDescompuesta is present, it should be displayed
        if (data.goldQuery.preguntaDescompuesta) {
          expect(container).toHaveTextContent('Pregunta Descompuesta:');
          expect(containsText(data.goldQuery.preguntaDescompuesta)).toBe(true);
        }

        // If metadata fields are present, they should be displayed
        if (data.goldQuery.sessionId || data.goldQuery.memberId || data.goldQuery.clasificacion) {
          expect(container).toHaveTextContent('Metadatos');
          
          if (data.goldQuery.sessionId) {
            expect(container).toHaveTextContent('ID de Sesión:');
            expect(containsText(data.goldQuery.sessionId)).toBe(true);
          }
          
          if (data.goldQuery.memberId) {
            expect(container).toHaveTextContent('ID de Miembro:');
            expect(containsText(data.goldQuery.memberId)).toBe(true);
          }
          
          if (data.goldQuery.clasificacion) {
            expect(container).toHaveTextContent('Clasificación:');
            expect(containsText(data.goldQuery.clasificacion)).toBe(true);
          }
        }
        
        // Clean up after this iteration
        cleanup();
      }),
      { 
        numRuns: 100,
        verbose: true
      }
    );
  });

  /**
   * Property test to verify component handles edge cases properly
   */
  test('Property 16 Edge Cases: Component handles minimal valid data', () => {
    const minimalDataArbitrary = fc.record({
      goldQuery: fc.record({
        id: fc.uuid(),
        chatInput: alphanumericString(1, 10),
        sessionId: fc.constant(undefined),
        memberId: fc.constant(undefined),
        clasificacion: fc.constant(undefined),
        preguntaDescompuesta: fc.constant(undefined),
        tablasColumnasDdl: alphanumericString(1, 10),
        sqlReference: alphanumericString(1, 10),
        createdAt: fc.date()
      }) as fc.Arbitrary<GoldQuery>,
      generatedSql: alphanumericString(1, 10)
    }) as fc.Arbitrary<QueryComparisonData>;

    fc.assert(
      fc.property(minimalDataArbitrary, (data) => {
        const { container } = render(<QueryComparison data={data} />);

        // Helper function to check if text is present, accounting for whitespace normalization
        const containsText = (text: string) => {
          const normalizedText = text.trim();
          return container.textContent?.includes(normalizedText) || false;
        };

        // All required fields should still be present even with minimal data
        expect(container).toHaveTextContent('Entrada del Chat:');
        expect(container).toHaveTextContent('Esquema de Tablas (DDL):');
        expect(container).toHaveTextContent('Consulta de Referencia (Gold)');
        expect(container).toHaveTextContent('Consulta Generada por IA');

        // Content should be displayed
        expect(containsText(data.goldQuery.chatInput)).toBe(true);
        expect(containsText(data.goldQuery.tablasColumnasDdl)).toBe(true);
        expect(containsText(data.goldQuery.sqlReference)).toBe(true);
        expect(containsText(data.generatedSql)).toBe(true);

        // Optional sections should not be present
        expect(container).not.toHaveTextContent('Pregunta Descompuesta:');
        expect(container).not.toHaveTextContent('Metadatos');
        
        // Clean up after this iteration
        cleanup();
      }),
      { 
        numRuns: 50,
        verbose: true
      }
    );
  });
});
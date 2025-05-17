# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file explains exactly how we'll store information about important things in our 
# project. It's like a recipe that tells us what details to include whenever we learn 
# about something new.

# High School Explanation:
# This document defines the standardized schema for knowledge entities in the TISIT 
# system. It outlines the specific fields, categorization approach, and hierarchical 
# organization that ensures consistent and comprehensive knowledge capture across 
# the entire repository.

# TISIT: Knowledge Entity Schema

## Overview

This document defines the standardized schema for storing knowledge entities in the TISIT system. By following this schema, we ensure that all captured knowledge is consistent, comprehensive, and properly categorized for efficient retrieval and use.

## Standard Entity Schema

Each knowledge entity in TISIT will be stored as a JSON document with the following structure:

```json
{
  "term": "String - The specific term or concept being documented",
  "context": "String - A single phrase representing the context of the term",
  "description": "String - A thorough explanation of the term within the given context",
  "considerations": "String - Key considerations or caveats related to the term",
  "category": "String - Precise categorization within the given context",
  "primary_domain": "String - The main domain of the term",
  "secondary_domain": "String - Secondary domain classification",
  "tertiary_domain": "String - Tertiary domain classification",
  "examples": [
    "String - Example 1",
    "String - Example 2",
    "...",
    "String - Example N"
  ],
  "references": [
    "String - Reference 1 (URL or citation)",
    "String - Reference 2 (URL or citation)",
    "...",
    "String - Reference N (URL or citation)"
  ],
  "books": [
    {
      "title": "String - Book Title in Title Case",
      "author": "String - Author Name in Title Case"
    },
    {
      "title": "String - Book Title in Title Case",
      "author": "String - Author Name in Title Case"
    }
  ],
  "people": [
    "String - Person 1",
    "String - Person 2",
    "...",
    "String - Person N"
  ],
  "related_terms": [
    "String - Related Term 1",
    "String - Related Term 2",
    "...",
    "String - Related Term N"
  ],
  "questions_and_answers": [
    {
      "question": "String - Question 1",
      "answer": "String - Answer 1"
    },
    {
      "question": "String - Question 2",
      "answer": "String - Answer 2"
    }
  ],
  "metadata": {
    "created_at": "ISO-8601 timestamp",
    "updated_at": "ISO-8601 timestamp",
    "created_by": "String - Creator identifier",
    "version": "String - Version number",
    "status": "draft|reviewed|published"
  }
}
```

## Field Guidelines

### Term
- Use the canonical name of the concept, technology, or person
- Maintain consistent capitalization (e.g., "Java" not "java")
- For acronyms, include the full name in parentheses (e.g., "API (Application Programming Interface)")

### Context
- Provide a single, specific phrase that frames the term
- Examples: "Programming Language", "Design Pattern", "Machine Learning Algorithm"
- Should be specific enough to disambiguate terms with multiple meanings

### Description
- Comprehensive explanation of the term within the context
- Should include:
  - Definition
  - Key characteristics
  - Historical background when relevant
  - Current significance or usage
  - Technical details when applicable

### Considerations
- Important caveats, limitations, or special considerations
- Common misconceptions
- Trade-offs or compromises
- Situational applicability

### Categorization
The three-tier domain classification provides hierarchical context:

#### Category
- Specific type within the context (e.g., "Object-Oriented" for Java in Programming Languages)

#### Primary Domain
- Highest-level domain (e.g., "Technology", "Business", "Science")

#### Secondary Domain
- Mid-level specification (e.g., "Software", "Finance", "Physics") 

#### Tertiary Domain
- Specific specialization (e.g., "Programming Languages", "Investment Strategies", "Quantum Mechanics")

### Examples
- Include 5-10 real-world examples
- Mix of common and specialized cases
- Include counterexamples when relevant
- Format each as a clear, concise statement

### References
- Include 5-10 authoritative sources
- Prioritize:
  - Official documentation
  - Influential papers or articles
  - High-quality tutorials or guides
  - Academic journals
  - Industry standards documents
- Format consistently as descriptive links

### Books
- Include 3-7 authoritative books on the subject
- Mix of foundational texts and advanced resources
- Follow consistent formatting:
  - Title in title case
  - Author in title case
  - (Optional) Year of publication

### People
- List 3-10 people closely associated with the term
- Include:
  - Creators/inventors
  - Major contributors
  - Leading experts
  - Influential practitioners
- Format consistently as full names

### Related Terms
- List 10-15 directly related terms
- Include:
  - Parent concepts
  - Sibling concepts
  - Component concepts
  - Competing alternatives
  - Complementary technologies/approaches

### Questions and Answers
- Include 5-10 thought-provoking Q&A pairs
- Cover diverse aspects:
  - Origins and history
  - Technical details
  - Advantages and disadvantages
  - Common use cases
  - Best practices
  - Controversies or debates
  - Future directions

### Metadata
- Automatically tracked system information
- Used for version control and provenance
- Facilitates review processes and auditing

## Creation Process

When adding a new knowledge entity to TISIT:

1. **Identification**: Determine the term and its relevant context
2. **Research**: Gather comprehensive information on all required fields
3. **Drafting**: Create initial entity document following the schema
4. **Review**: Verify completeness, accuracy, and adherence to format
5. **Publishing**: Add to the knowledge repository
6. **Linking**: Establish connections to related terms

## Example Entity

Here's an example entity for "Java" in the context of "Programming Language":

```json
{
  "term": "Java",
  "context": "Programming Language",
  "description": "Java is a high-level, class-based, object-oriented programming language designed to have as few implementation dependencies as possible. It was originally developed by James Gosling at Sun Microsystems (later acquired by Oracle) and released in 1995. Java applications are compiled to bytecode that can run on any Java Virtual Machine (JVM) regardless of the underlying computer architecture, making it platform-independent. Java is known for its 'write once, run anywhere' (WORA) principle, strongly-typed nature, automatic memory management through garbage collection, and comprehensive standard library.",
  "considerations": "While Java offers platform independence and strong security features, it often requires more memory and may have slower startup times compared to natively compiled languages. Its verbose syntax can lead to more code compared to modern languages. The JVM requires installation on the target system, and Java's garbage collection, while convenient, can cause unpredictable pauses in application execution.",
  "category": "Object-Oriented",
  "primary_domain": "Technology",
  "secondary_domain": "Software Development",
  "tertiary_domain": "Programming Languages",
  "examples": [
    "Android mobile applications (Android SDK is Java-based)",
    "Enterprise backend systems using Spring Framework",
    "Web applications using JavaServer Pages (JSP) and Servlets",
    "Large-scale data processing with Apache Hadoop",
    "Cross-platform desktop applications with JavaFX",
    "Financial services applications requiring high reliability",
    "Embedded systems in set-top boxes and smart cards",
    "High-frequency trading systems in financial institutions",
    "Scientific applications using numerical computing libraries",
    "Internet of Things (IoT) applications on capable devices"
  ],
  "references": [
    "Oracle Java Documentation: https://docs.oracle.com/en/java/",
    "Java Language Specification: https://docs.oracle.com/javase/specs/",
    "OpenJDK: https://openjdk.org/",
    "Java Tutorials (Oracle): https://docs.oracle.com/javase/tutorial/",
    "Java Platform, Standard Edition (Java SE) API: https://docs.oracle.com/en/java/javase/17/docs/api/",
    "Baeldung Java Guides: https://www.baeldung.com/",
    "Java World: https://www.javaworld.com/",
    "JavaRanch Community: https://coderanch.com/",
    "Java Magazine: https://blogs.oracle.com/javamagazine/",
    "IBM Developer Java: https://developer.ibm.com/languages/java/"
  ],
  "books": [
    {
      "title": "Effective Java",
      "author": "Joshua Bloch"
    },
    {
      "title": "Java Concurrency in Practice",
      "author": "Brian Goetz"
    },
    {
      "title": "Core Java Volume I - Fundamentals",
      "author": "Cay S. Horstmann"
    },
    {
      "title": "Head First Java",
      "author": "Kathy Sierra and Bert Bates"
    },
    {
      "title": "Java Performance: The Definitive Guide",
      "author": "Scott Oaks"
    },
    {
      "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
      "author": "Robert C. Martin"
    },
    {
      "title": "Thinking in Java",
      "author": "Bruce Eckel"
    }
  ],
  "people": [
    "James Gosling (Creator of Java)",
    "Brian Goetz (Java Language Architect at Oracle)",
    "Joshua Bloch (Former Java Chief Architect at Google)",
    "Doug Lea (Concurrency expert and java.util.concurrent package designer)",
    "Martin Odersky (Created Scala, worked on Java generics)",
    "Venkat Subramaniam (Java Champion and influential educator)",
    "Heinz Kabutz (Java Concurrency expert)",
    "Adam Bien (Java EE expert)",
    "Trisha Gee (Java Champion and JVM advocate)",
    "Mark Reinhold (Chief Architect of the Java Platform Group at Oracle)"
  ],
  "related_terms": [
    "JVM (Java Virtual Machine)",
    "Bytecode",
    "Kotlin",
    "Scala",
    "Garbage Collection",
    "Object-Oriented Programming",
    "Spring Framework",
    "JavaFX",
    "Java EE/Jakarta EE",
    "Maven",
    "Gradle",
    "JUnit",
    "JDBC",
    "Servlets",
    "Java Collections Framework"
  ],
  "questions_and_answers": [
    {
      "question": "What makes Java platform-independent?",
      "answer": "Java achieves platform independence through its 'write once, run anywhere' approach. Java code is compiled into bytecode, which is then executed by the Java Virtual Machine (JVM) rather than directly by the operating system. Since JVMs are available for most operating systems, the same bytecode can run on different platforms without modification."
    },
    {
      "question": "How does Java manage memory?",
      "answer": "Java manages memory through automatic garbage collection. When objects are no longer referenced by any part of the program, the garbage collector automatically reclaims the memory. This eliminates the need for manual memory management and helps prevent memory leaks and pointer errors common in languages like C and C++."
    },
    {
      "question": "What are the key differences between Java and similar languages like C++?",
      "answer": "Unlike C++, Java has no pointers (though it has references), no multiple inheritance (it uses interfaces instead), no operator overloading (except for String concatenation), and no manual memory management. Java is strictly object-oriented (no standalone functions), has automatic garbage collection, and runs on a virtual machine rather than compiling to native code directly."
    },
    {
      "question": "How has Java evolved since its creation in 1995?",
      "answer": "Java has evolved significantly, moving from version 1.0 to the current version 17 (as of 2023). Major evolutions include: the addition of generics (Java 5), annotations (Java 5), lambda expressions (Java 8), modules (Java 9), local variable type inference (Java 10), records (Java 14), sealed classes (Java 15), and pattern matching (Java 16+). The release cycle has also changed from irregular major releases to a predictable six-month release cadence with long-term support (LTS) versions every two years."
    },
    {
      "question": "What are Java's primary use cases today?",
      "answer": "Java remains widely used for enterprise applications, Android mobile development, web services and applications, big data processing frameworks (like Hadoop and Spark), financial applications, scientific computing, and embedded systems. Its combination of performance, reliability, security, and extensive ecosystem makes it particularly valuable for large-scale, mission-critical systems."
    },
    {
      "question": "What challenges does Java face in the modern programming landscape?",
      "answer": "Java faces challenges including: competition from more concise languages (like Kotlin, Python), performance overhead compared to native languages, relatively slow startup time (though improving with features like Project Leyden), verbosity compared to modern alternatives, and keeping pace with rapid industry changes while maintaining backward compatibility."
    },
    {
      "question": "What is the significance of OpenJDK?",
      "answer": "OpenJDK is the open-source reference implementation of the Java Standard Edition platform. Its significance lies in providing a free and open alternative to Oracle's commercial JDK, ensuring Java remains accessible to all developers. Most Java distributions today, including Oracle's own, are based on OpenJDK. This has helped Java remain relevant and widely adopted despite changes in Oracle's licensing model."
    }
  ],
  "metadata": {
    "created_at": "2025-05-17T15:30:00Z",
    "updated_at": "2025-05-17T15:30:00Z",
    "created_by": "system",
    "version": "1.0",
    "status": "published"
  }
}
```

## Implementation Notes

### Storage Strategy

Knowledge entities will be stored as individual JSON files in a Git-tracked directory structure:

```
/tisit/
  /entities/
    /technology/
      /programming_languages/
        java.json
        python.json
      /frameworks/
        react.json
    /business/
      /methodologies/
        agile.json
```

### Retrieval Strategy

Entities can be retrieved through:

1. **Direct access** - by term and context
2. **Domain browsing** - by navigating the domain hierarchy
3. **Full-text search** - by querying content across all fields
4. **Relationship exploration** - by following related terms

### Automation

To facilitate entity creation:

1. **Templates** - Provide skeleton JSON with all required fields
2. **CLI tools** - Command-line interface for adding/updating entities
3. **AI assistance** - Leverage Claude to generate entity drafts
4. **Validation** - Automatic schema validation to ensure consistency
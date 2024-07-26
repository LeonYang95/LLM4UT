# Running Examples of Our Study.

## Prompt Design

### Natural Language Description

Below is an example prompt used for DeepSeek-Coder models.

    ### Instruction:
    Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.
    
    The focal method belongs to the class `org.jfree.data.DefaultKeyedValues2D`, and the constructors are:
    ```
    public DefaultKeyedValues2D(boolean sortRowKeys);
    public DefaultKeyedValues2D(); 
    ```
    These are the fields defined in the class:
    ```
    private static final long serialVersionUID = -5514169970951994748L;
    private boolean sortRowKeys;
    ...
    ```
    These are the methods defined in the class :
    ```
    public List getColumnKeys();
    public void setValue(Number value, Comparable rowKey, Comparable columnKey);
    public void removeColumn(int columnIndex);
    public void removeRow(int rowIndex);
    ...
    ```
    This is the method that you are going to test.
    ```
    public void removeColumn(Comparable columnKey) {
        ...
    }
    ```
    The parameter of the method is `columnKey`.
    The parameters come from class `Comparable`.
    Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.
    
    ### Response:
    ```java
    import org.junit.Test;
    import org.junit.Assert;
    import org.junit.Before;
    。。。
    import org.jfree.chart.util.ObjectUtilities;
    import org.jfree.chart.util.PublicCloneable;
    
    public class DefaultKeyedValues2DTest{


### Code Language Description

Below is an example prompt used for DeepSeek-Coder models.


    ### Instrucion
    Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.
    ```
    // The method belongs to the class:
    org.jfree.data.DefaultKeyedValues2D
    
    // Fields
    private static final long serialVersionUID = -5514169970951994748L;
    private boolean sortRowKeys;
    ...
    
    // Other methods
    public List getColumnKeys();
    public void setValue(Number value, Comparable rowKey, Comparable columnKey);
    public void removeColumn(int columnIndex);
    public void removeRow(int rowIndex);
    ...
    
    // The following code is the method that you are going to test.
    public void removeColumn(Comparable columnKey) {
        ...
    }
    
    // The parameter of the method:
    columnKey
    
    // The parameters come from:
    Comparable
    ```
    Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.
    
    ### Response:
    ```java
    import org.junit.Test;
    import org.junit.Assert;
    import org.junit.Before;
    ...
    import org.jfree.chart.util.ObjectUtilities;
    import org.jfree.chart.util.PublicCloneable;
    
    public class DefaultKeyedValues2DTest{


## Prompt with In-Context-Learning Techniques.


Below is an example prompt used for DeepSeek-Coder model using CoT and code language description. 

For the target method `removeDomainMarker`, the LLM is intructed to summarize the intension of the method and then generate unit tests.

````
### Instruction:
Your Task is to write some unit tests. Please first understand the intent of the target method, the method you are going to test is at the end of the instruction.
```
// The method belongs to the class:
org.jfree.chart.plot.CategoryPlot

// Constructor:
public CategoryPlot();
public CategoryPlot(CategoryDataset dataset, CategoryAxis domainAxis, ValueAxis rangeAxis, CategoryItemRenderer renderer);

// Fields
private static final long serialVersionUID = -3537691700434728188L;
public static final boolean DEFAULT_DOMAIN_GRIDLINES_VISIBLE = false;
public static final boolean DEFAULT_RANGE_GRIDLINES_VISIBLE = true;
...

// Other methods
public void setRangeAxisLocation(int index, AxisLocation location, boolean notify);
public void addRangeMarker(Marker marker, Layer layer);
public CategoryAnchor getDomainGridlinePosition();
...

// The following code is the method that you are going to test.
public boolean removeDomainMarker(int index, Marker marker, Layer layer, boolean notify) {
    ArrayList markers;
    if (layer == Layer.FOREGROUND) {
        markers = (ArrayList) this.foregroundDomainMarkers.get(new Integer(index));
    } else {
        markers = (ArrayList) this.backgroundDomainMarkers.get(new Integer(index));
    }
    if (markers == null) {
        return false;
    }
    boolean removed = markers.remove(marker);
    if (removed && notify) {
        fireChangeEvent();
    }
    return removed;
}
```
Please infer the intention of the removeDomainMarker method.
### Response:
<The intention inferred by LLM>

### Instruction:
<The intention inferred by LLM>

You are a professional who writes Java test methods. Please write some unit tests for the removeDomainMarker method with the given intention.
You should write unit tests with maximizing both branch and line coverage. Please use Java 1.7 and Junit 4 and make sure that the output format is Markdown, and no explainations needed.

### Response:
```java
import org.junit.Test;
import org.junit.Assert;
import org.junit.Before;
import org.junit.After; 
...

public class CategoryPlotTest{
````



### Retrieval-Augmented Generation (RAG)

Below is an example prompt used for DeepSeek-Coder model using RAG and natural language description. 

For the target method `removeColumn`, the retrieved example is the method `previous` and its unit test `testW52Y9999Previous`.

````
### Instruction:
Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.

The focal method belongs to the class `org.jfree.data.DefaultKeyedValues2D`, and the constructors are:
```
public DefaultKeyedValues2D(boolean sortRowKeys);
public DefaultKeyedValues2D(); 
```
These are the fields defined in the class:
```
private static final long serialVersionUID = -5514169970951994748L;
private boolean sortRowKeys;
...
```
These are the methods defined in the class :
```
public List getColumnKeys();
public void setValue(Number value, Comparable rowKey, Comparable columnKey);
public void removeColumn(int columnIndex);
public void removeRow(int rowIndex);
...
```
Here is an example of a similar focal method and its unit test:
```
// The following code is an example focal method.
public RegularTimePeriod previous() {
		...
}
// The following code is the cooresponding unit test generated for the example method.
public void testW52Y9999Previous() {
		Week previous = (Week) this.w52Y9999.previous();
		assertEquals(this.w51Y9999, previous);
}
```

This is the method that you are going to test.
```
public void removeColumn(Comparable columnKey) {
    ...
}
```
The parameter of the method is `columnKey`.
The parameters come from class `Comparable`.
Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.

### Response:
```java
import org.junit.Test;
import org.junit.Assert;
import org.junit.Before;
...
import org.jfree.chart.util.ObjectUtilities;
import org.jfree.chart.util.PublicCloneable;

public class DefaultKeyedValues2DTest{
````


## Illustration Examples of Reasons of Undetected Defects.

### Insufficient Test Coverage

### Missing Specific Inputs

### Improper Assertion


